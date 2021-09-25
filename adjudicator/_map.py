""" The Map class

"""

from json import load as json_load

from collections import ChainMap

from adjudicator import Force, Geography, Location, Province

from lib.errors import MapError
from lib.classes import make_instances
from lib.lists import attr_select, flatten


class Map:
    """ A game map / game board.

    Parameters
    ----------
    name : string
        The name of the map. Should match the filename of the
        corresponding JSON file in the `maps` folder.

    Attributes
    ----------
    name : string
        The name of the map.

    loaded : boolean
        Whether the information from the JSON file has been read
        into the instance. See Notes.

    forces : list of Forces
        The list of forces that can appear on this map.

    orders : list of strings
        The list of orders that can be used on the map.

    geographies : list of Geographies
        The list of Geographies that appear on the map.  
  
    provinces : list of Provinces
        The list of Provinces that appear on the map.
    
    locations : list of Locations
        The list of Locations that appear on the map.
    
    force_dict : dictionary
        A dictionary whose keys are short forms, and values are full
        forms, of Forces appearing on the map.

    abbreviations : dictionary
        A dictionary whose keys are short forms, and values are full
        forms, of Provinces appearing on the map, 

    supply_centers : list of Provinces
        A list of all provinces that are supply centers.

    Notes
    -----
    The information in the corresponding JSON file in the `maps`
    folder is not read into the instance at initiation, but is
    read when the `load` method is called.

    """

    def __init__(self, name):
        """ Constructor.

        """
        self.name = name
        self.loaded = False

    def __str__(self):
        """ Print format.

        """
        return self.name

    def info(self, string):
        """ Retrieves information as a string.

        """
        return list(map(str, getattr(self, string)))

    def load(self):
        """ Loads the map information from the JSON file in the
        maps folder.

        """
        with open(f'maps/{self.name}.json') as file:
            data = json_load(file)

        self.orders = tuple(data['orders'])

        # Create all class instances
        self.forces = make_instances(
            data['forces'],
            Force
        )
        
        self.provinces = make_instances(
            data['provinces'],
            Province
        )

        self.geographies = make_instances(
            data['geographies'],
            Geography,
            map=self
        )

        self.locations = make_instances(
            data['locations'],
            Location,
            map=self
        )

        # Retrieve the short form dictionaries.
        self.force_abbreviations = dict(ChainMap(
            *[force.short_forms for force in self.forces]
        ))
        self.abbreviations = {
            province.short: f'{province}' for province in self.provinces
        }

        # Retrieve the list of supply centers.
        self.supply_centers = tuple(
            attr_select(self.provinces, 'supply_center')
        )

        # Consistency checks
        id_check = {
            self.locations[k].id == k 
            for k in range(len(self.locations))
        }
        if False in id_check:
            raise MapError("Location id's doesn't match `map.locations` indices.")

        self.loaded = True

    def instance(self, name, class_):
        """ Finds the instance of a given class with a given name.

        """
        # This list should maybe not be hard coded...
        attributes = {Force: 'forces',
                      Geography: 'geographies',
                      Province: 'provinces'}

        try:
            objects = getattr(self, attributes[class_])
        except KeyError:
            objects = getattr(self, class_)
    
        return next((obj for obj in objects if obj.name == name),
                    None)

    def instances(self, lst, class_):
        """ Finds the instances of a given class with given names.
        
        """
        return [self.instance(name, class_) for name in lst]

    def locations_of(self, province):
        """ Returns all locations attached to a given province.

        """
        return attr_select(self.locations, 'province', province)

    def locate(self, force, identifier, origin=None,
               specifier=None, either=False):
        """ Returns a location identified by partial data.

        Parameters
        ----------
        force : Force
            The force of the unit associated with the location.

        identifier : integer or Province or string
            An object used to identify the location. If it is an integer,
            then it is interpreted as the `id` of the location. If it is
            a Province, then it is interpreted as the province that the
            location is associated with. If it is a string, then it is
            interpreted as the name of either the location itself, or of
            the province associated with the location.
            
        origin : Location, default=None
            The origin of a unit trying to move to the location. Can help
            distinguish between coastal locations of the same province.

        specifier : string, default=None
            A specifier that should appear in the name of the location.

        either : boolean
            Whether an ambiguous return is allowed. If true, then the first
            location from `self.locations` that fits the description will
            be returned.

        Notes
        -----
        If at any step only one candidate location remains in the search,
        then that location will be returned, even if it does not match all
        descriptions. This is on purpose.

        """
        # The first case is if the identifier is the location id.
        if isinstance(identifier, int):
            return self.locations[identifier]
        
        # In the second case is if the identifier is a province or the
        # name of a province or location.
        locations = [loc for loc in self.locations
                     if loc.named(str(identifier))
                     and loc.force == force]

        # Filter by reachable from origin location
        if len(locations) > 1 and origin is not None:
            locations = [loc for loc in locations
                         if origin.id in loc.connections]

        # Filter by specifier.
        if len(locations) > 1 and specifier is not None:
            locations = [loc for loc in locations
                         if loc.name == f'{identifier} {specifier}']

        # Throw an error if the results is ambiguous
        if len(locations) > 1 and not either:
            raise MapError(
                f'There are at least two locations in {identifier} '
                'matching the given criteria.'
            )

        try:
            return locations[0]

        except IndexError:
            return None  # No available location.

    def one_adjacent(self, locations, province):
        """ Tests if one location from a list of locations is adjacent to
        one location associated to a given province.
        
        """
        return next((True for loc in locations
                     if loc.reaches_province(province)),
                    False)

    def has_path(self, source, target, via):
        """ Tests if there is a path from a source province to a target 
        province via a set of given locations. 
        
        This method is used to look for possible convoy paths. Notice that
        if there is no path, then the method returns `False`, even if the
        two provinces are adjacent. This is intentional.

        The algorithm is by graph contractions, and does not identify the
        explicit path. Checking for explicit paths is much slower.

        """
        # Identify all location adjacent to the source province and
        # check if we can reach the target using only one `via` location.
        reached = [loc for loc in via if loc.reaches_province(source)]
        arrived = self.one_adjacent(reached, target)

        # Iteratively expand the set of location that we have reached.
        new = reached
        while not arrived and len(new) > 0:

            # Find the locations that we reach in this step.
            ids = flatten([loc.connections for loc in new])
            new = [loc for loc in via if loc.id in ids 
                   and loc not in reached]
            
            # Check if we can arrive at the target.
            arrived = self.one_adjacent(new, target)

            # Remember all locations that we've reached so far. 
            reached = reached + new

        return arrived
