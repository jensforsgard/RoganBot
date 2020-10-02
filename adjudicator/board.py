#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Imports
# =============================================================================

import json


# =============================================================================
# Functions
# =============================================================================

def flatten(lists):
    """ Flattens a list of lists on the first level.

    """
    return [item for sublist in lists for item in sublist]


def despecify(string, geography):
    """ Removes the specifiers of the geography from the string.

    """
    for specifier in geography.force.specifiers:
        string = string.replace(f' {specifier}', '')
    return string


def first_named(objects, name):
    """ From a list of objects, return the first object with a given name.

    """
    generator = (obj for obj in objects if obj.name == name)
    return next(generator, None)


def union(dictionary_list):
    """ Joins a list of dictionaries into one dictionary.

    """
    answer = {}
    for entry in dictionary_list:
        answer.update(entry)
    return answer


def make_instances(dictnry, class_, obj=None):
    """ Creates a list of instances of a class whose identifiers are the
    keys of the dictionary and properties are given by the values of the
    dictionary.

    Parameters
    ----------
    dictionary : dictionary
        A dictionary whose keys are identifiers of the instances and whose
        values are dictionaries holding the properties of the instances.
    class_ : type
        The type of the instances which are to be created.
    obj : object, optional
        An object containing necessary information to initiate the instances.

    """
    if obj is None:
        return [class_(key, dictnry[key]) for key in dictnry.keys()]
    else:
        return [class_(key, dictnry[key], obj) for key in dictnry.keys()]


# =============================================================================
# Error Classes
# =============================================================================

class MapError(Exception):

    def __init__(self, message):

        self.message = message


# =============================================================================
# The Province Class
# =============================================================================

class Province:
    """ A province is a region of the map. Besides identifiers, the main
    property of a province is whether it is a supply center or not.

    Attributes:
        id : integer
            The id of the province.
        name : string
            The name of the province. Names of provinces should be unique, and
            are used as the primary identifier of a province.
        short_form : string
            The three letter abbreviation of the name of the province,
            pssibly preceded and succeeded by spaces.
        supply_center : boolean
            Marks whether the province contains a supply center.

    """

    def __init__(self, number, dctnry):
        """ The constructor for the Province class.

        Parameters
        ----------
        number : integer
            The id number of the province.
        dctnry : dictionary
            A dictionary including the remaining properties.

        """
        self.id = int(number)
        self.name = dctnry['name']
        self.short_form = dctnry['short']
        self.supply_center = dctnry['supply center']

    def __str__(self):
        """ Print format.

        """
        return self.name


# =============================================================================
# The Geography Class
# =============================================================================

class Geography:
    """ A Geography is a container of a unit. The geography specifies which
    classes of orders that are available for the unit it contains.

    Attributes:
        name : string
            The name of the geography. Names should be unique and are used
            as identifiers for geographies.
        force : Force
            Specifying the class instance of attribut 'force' of a unit which
            is contained in the geography.
        orders : list of strings
            The list of orders, encoded by their names as strings, which are
            available for a unit currently contained in the Geography.

    """

    def __init__(self, name, dctnry, map_):
        """ The constructor for the Geography class.

        Parameters
        ----------
        name : string
        dctnry : dictionary
            Containing the remaining properties.
        map_ : Map
            The game map, necessary to initate the force attribute.
        """
        self.name = name
        self.force = map_.instance(dctnry['unit'], Force)
        self.orders = dctnry['orders']

    def __str__(self):
        """ Print format.

        """
        return self.name


# =============================================================================
# The Location Class
# =============================================================================

class Location:
    """ A location is a geography attached to a province. That is, it's a
    container of a unit attached to a province of the map. The location
    spacifies which other locations that are adjacent (i.e., reachable).

    Attributes:
        id : integer
            The id of the location. The id should be unique and is used as the
            identifier of the location.
        name : string
            The name of the location. Names of locations are not necessarily
            unique and can not act as identifier for locations.
        geography : Geography
            The geography of the location.
        force : Force
            The unit type which may be present in the location. Agrees with
            the unit type associated to the geography.
        province : Province
            The province associated with the location.
        connections : list of integers
            A list of all locations which can be reached (i.e., adjacent) from
            the instance. Reachable locations are encoded by their id.

    """

    def __init__(self, number, dctnry, map_):
        """ The constructor for the Location class.

        Parameters
        ----------
        number : integer
            The id of the location.
        dctnry : dictionary
            Containing the remaining defining properties.
        map_ : Map
            The current map, nessecary to find the geography instance and the
            province instance associated with the location.

        """
        self.id = int(number)
        self.name = dctnry['name']
        self.connections = dctnry['connections']
        # Retrieve the geography and the force
        self.geography = map_.instance(dctnry['geography'], Geography)
        self.force = self.geography.force
        # Retrieve the province
        province_name = despecify(self.name, self.geography)
        self.province = first_named(map_.provinces, province_name)

    def __str__(self):
        """ Print format.

        """
        return self.name

    def reaches_location(self, location):
        """ Tests if the instance reaches a given location.

        Parameters
        location : Location or integer
            Either a location of a location id.

        """
        if type(location) is int:
            return location in self.connections
        elif type(location) is Location:
            return location.id in self.connections
        raise TypeError('Input is neither a location nor a location id.')

    def reaches_province(self, board, province):
        """ Tests if the instance reaches any location associated to a given
        province. Needs the current game map as input in order to find all
        locations associated to the province.

        Parameters
        ----------
        board : Map
        province : Province or string
            Either the province or the name of the province.

        """
        province_locations = board.locations_of(province)
        for location in province_locations:
            if location.id in self.connections:
                return True
        return False

    def named(self, name):
        """ Tests if the instance is associated with the given name; it may
        either be the name of the instance or the name of the province
        associated with the instance.

        Parameters
        ----------
        name : string

        """
        return self.name == name or self.province.name == name


# =============================================================================
# The Force Class
# =============================================================================

class Force:
    """ A Force is a type of unit. The force specifies which geographies the
    unit can be located in, and it specifies which orders the unit can be the
    object of.

    Attributes:
        name : string
            The name of the force.
        may_receive : list of strings
            List of orders, presented as strings, which a unit of the given
            force can be the object of.
        specifiers : list of strings
            List of specifiers of locations which can hold a unit of the given
            force. Specifiers are only used if a province has multiple
            locations that can hold units of a force.
        short_forms : dictionary
            A dictionary with specifier short forms as keys and specifier full
            forms as values.

    """

    def __init__(self, name, dctnry):
        """ The constructor for the Force class.

        Parameters
        ----------
        name : string
        dctnry : dictionary
            A dictionary containing the remaining information.

        """
        self.name = name
        self.may_receive = dctnry['may receive']
        self.specifiers = dctnry['specifiers']
        self.short_forms = dict(zip(dctnry['short forms'], self.specifiers))

    def __str__(self):
        """ Print format.

        """
        return self.name


# =============================================================================
# The Map Class
# =============================================================================

class Map:
    """ A game map.

    Attributes:
        name : string
            The name of the map. Identifies the JSON file form which the
            information will be retrieved.
        forces : list of forces
            A list of possible forces of units on the map.
        orders : list of strings
            A list of orders which may be used on the given map.
        geographies : list of Geographies
            A list of geographies appearing on the map.
        provinces : list of Provinces
            A list of provinces appearing on the map.
        locations : list of Locatinos
            A list of locations appearing on the map.
        forces_dict : dictionary
            A dictionary with short forms of geography specifiers as keys
            and full forms as values.
        province_dict : dictionary
            A dictionary of short forms of province names as keys (preceded
            and succeeded by spaces) and full form province names (preceded
            ans succeeded by spaces) as values.
        supply_centers : list of Provinces
            A list of the provinces which contain supply centers.

    """

    def __init__(self, name):
        """ The constructor for the Map class.

        Parameters
        ----------
        name : string

        """
        self.name = name
        self.forces = []
        self.orders = []
        self.geographies = []
        self.provinces = []
        self.locations = []
        self.forces_dict = {}
        self.province_dict = {}
        self.supply_centers = []

    def __str__(self):
        """ Print format.

        """
        return self.name

    def display(self, string):
        """ Prints some entities associated to the map.

        Parameters
        ----------
        string : string
            The entities to be displayed.

        """
        if string == 'provinces':
            print([province.name for province in self.provinces])
            return
        if string == 'supply centers':
            print([province.name for province in self.provinces if
                    province.supply_center])
            return
        if string == 'abbreviations':
            for entry in self.province_dict.keys():
                print(f'{entry} {self.province_dict[entry]}')
            return

    def load(self):
        """ Loads the map information from the JSON file in the maps folder
        with the name of the map in the maps folder.

        """
        with open(f'maps/{self.name}.json') as file:
            data = json.load(file)
            file.close()
        assert self.name == data['name']  # Check that the file is not corrupt
        self.orders = data['orders']
        self.forces = make_instances(data['forces'], Force)
        self.geographies = make_instances(data['geographies'], Geography, self)
        self.provinces = make_instances(data['provinces'], Province)
        self.locations = make_instances(data['locations'], Location, self)
        # Compute the short form dictionaries.
        self.forces_dict = union([force.short_forms for force in self.forces])
        self.province_dict = {province.short_form: f'{province.name}'
                              for province in self.provinces}
        # Compute the list of supply centers.
        self.supply_centers = [province for province in self.provinces
                               if province.supply_center]

    def instance(self, name, class_type):
        """ Finds the instance of a given class with a given name.

        """
        # This list should maybe not be hard coded. Location does not appear
        # in the list as they are not identified by name.
        attributes = {Force: 'forces',
                      Geography: 'geographies',
                      Province: 'provinces'}
        objects = getattr(self, attributes[class_type])
        return next((obj for obj in objects if obj.name == name), None)

    def locations_of(self, province):
        """ Returns all locations attached to a given province.

        """
        return [location for location in self.locations
                if location.province is province]

    def locate(self, force, name, origin=None, specifier=None):
        """ Returns a location identified by partial data.

        Parameters
        ----------
        force : Force
            The force associated with the location.
        name : string
        origin : Location, optional
            An origin location which the returned location must reach.
        specifier : string, optional
            A specifier which the location should have.

        Returns
        -------
        Location or None
        """
        locations = [location for location in self.locations
                     if location.named(name)
                     and location.force == force]
        # Filter by reachable from origin location
        if len(locations) >= 2 and origin is not None:
            locations = [location for location in locations
                         if origin.id in location.connections]
        # Filter by specified coast.
        if len(locations) >= 2 and specifier is not None:
            locations = [location for location in locations
                         if location.name == name + ' ' + specifier]
        assert len(locations) < 2, ('There are at least two locations in '
                                    f'{name} matching the given criteria.')
        if len(locations) == 1:
            return locations[0]
        else:
            return None  # Signals that there is no available location.

    def has_path(self, source, target, via):
        """ Tests if there is a path from source to target via the given
        locations. N.B., it does not suffice that source is adjacent to target.

        Parameters
        ----------
        source : Province
        target : Province
        via : list of Locations

        Raises
        ------
        MapError : If the algorithm does not terminate.

        Returns
        -------
        arrived : boolean

        """
        # Find the locations we can reach in one step.
        reached = [location for location in via
                   if location.reaches_province(self, source)]
        # Test if we can reach the target from one of those locations.
        arrived = True in [location.reaches_province(self, target)
                           for location in reached]
        counter = 1  # Counting, in case the algorithm does not terminate.
        while not arrived and counter <= len(via) + 2:
            ids = flatten([location.connections for location in reached])
            # Find the new reached locations in this step.
            new = [location for location in via
                   if location.id in ids and location not in reached]
            # If no new locations was reached, then the search failed.
            if len(new) == 0:
                break
            # Test if we can reach the target from any of the new locataions.
            arrived = True in [location.reaches_province(self, target)
                               for location in new]
            # Update the list of already reached locations.
            reached = reached + new
            counter += 1
        if counter >= len(via) + 2:
            raise MapError('Map method has_path algorithm was inconclusive.')
        return arrived

    def check_consistency(self):
        """ Checks whether the attributes of the map are consistent with
        eachother. The purpose is to find errors in the map files.

        Raises
        ------
        MapError : If there are inconsistencies.

        """
        for geography in self.geographies:
            if geography.force not in self.forces:
                raise MapError(f'Geography {geography} allows a force which is'
                               ' not recognized by the map.')
            if not set(geography.orders).issubset(self.orders):
                raise MapError(f'Geography {geography} allow a set of orders '
                               'which is not recognized by the map.')
        provinces = {location.province for location in self.locations}
        if set(self.provinces) != provinces:
            raise MapError('There is a location whose province is not listed.')
        for location in self.locations:
            reached = [self.locations[k].connections
                       for k in location.connections]
            if False in [location.id in entry for entry in reached]:
                raise MapError(f'Location with id {location.id} has an '
                               'inconsistent connection.')


# =============================================================================
# The Season Class
# =============================================================================

class Season:
    """ The class that keeps track of the season of the game.

    Attributes:
        name : string
            The name of the season.
        phase : string
            The name of the phase.
        year : integer
            The year.

    """

    def __init__(self, name, phase, year):
        """ The constructor for the Season class.

        Parameters
        ----------
        name : string
        phase : string
        year : integer

        """
        self.name = name  # ['Spring', 'Fall']
        self.phase = phase  # ['Pregame', 'Diplomacy', 'Retreats', 'Builds', 'Postgame']
        self.year = year  # integer

    def __str__(self):
        if self.phase == 'Pregame':
            return 'Pregame.'
        elif self.phase == 'Builds':
            return f'Builds in {str(self.year)}.'
        else:
            return f'{self.phase} in {self.name} {str(self.year)}.'

    def progress(self):
        """ Moves the season forward one phase.

        """
        if self.phase == 'Diplomacy':
            self.phase = 'Retreats'
        elif self.phase == 'Retreats' and self.name == 'Spring':
            self.name = 'Fall'
            self.phase = 'Diplomacy'
        elif self.phase == 'Retreats' and self.name == 'Fall':
            self.phase = 'Builds'
        elif self.phase == 'Builds':
            self.name = 'Spring'
            self.phase = 'Diplomacy'
            self.year += 1
        elif self.phase == 'Pregame':
            self.phase = 'Diplomacy'

    def regress(self):
        """ Moves the season backwards one phase. Possible bug: will not
        recognize when it hits 'Pregame'.

        """
        if self.phase == 'Builds':
            self.phase = 'Retreats'
        elif self.phase == 'Retreats':
            self.phase = 'Diplomacy'
        elif self.phase == 'Diplomacy' and self.name == 'Fall':
            self.phase = 'Retreats'
            self.name = 'Spring'
        elif self.phase == 'Diplomacy' and self.name == 'Spring':
            self.name = 'Fall'
            self.phase = 'Builds'
            self.year -= 1
    
    def conclude(self):
        self.phase = 'Postgame'
        self.name = '-'
        
        
