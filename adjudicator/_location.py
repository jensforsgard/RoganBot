""" The Location class

"""

from adjudicator import Geography
from lib.classes import despecify
from lib.lists import first_named

class Location:
    """ A location is a geography paired with a province. That is,
    it is a container for a specified unit type, attached to a
    region of the game map.

    Parameters
    ----------
    id : integer
        The id of the location.

    name : string
        The name of the location.

    connections : list of integers
        The list of adjacent locations, identified by `id`.

    geography : string
        The name of the geography associated with the location.
    
    map: Map
        The game map.

    Attributes
    ----------
    id : integer
        See Parameters.

    name : string
        See Parameters.

    connections : tuple of integers
        The tuple of adjacent locations, identified by `id`.

    map: Map
        See Parameters.

    geography : Geography
        The geography instance associated with the location.
    
    force : Force
        The unit force instance associated with the location.
        An alias for `geography.force`

    province : Province
        The province instance associated with the location.

    Notes
    -----
    The location specifies adjacencies.

    Locations are identified by `id`. The name of the location is
    not necessarily unique.

    The Province associated with the location is deduced from the
    location name, by removing specifiers associated with the given
    geography.

    """

    def __init__(self, id, name, connections, geography, map):
        """ Constructor.

        """
        self.id = int(id)
        self.name = name
        self.connections = tuple(connections)
        self.map = map

        self.geography = map.instance(geography, Geography)
        self.force = self.geography.force

        self.province = first_named(
            map.provinces,
            despecify(self.name, self.geography)
        )

    def __str__(self):
        """ Print format.

        """
        return self.name

    def reaches_location(self, location):
        """ Tests if the instance reaches a given location, where the
        parameter `location` can be either an instance of the 
        Location class, or an integer.

        """
        try:
            return location.id in self.connections

        except AttributeError:
            return location in self.connections

    def reaches_province(self, province):
        """ Tests if the instance reaches any location associated with 
        a given province.

        Might be rewritten to also allow string inputs (province names),
        but there is currently no need.

        Uses that the id of a location is equal to its position in the
        list `self.map.locations`.

        """
        return province in [self.map.locations[k].province
                            for k in self.connections]

    def named(self, name):
        """ Tests if the instance is associated with the given name.

        """
        return self.name == name or self.province.name == name
