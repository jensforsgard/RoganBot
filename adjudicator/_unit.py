""" The Unit class

"""

class Unit:
    """ An unit is a playing piece, located on the map, and
    belonging to one of the players.

    Parameters
    ----------
    id : integer
        The id number of the unit. Should be unique.

    owner : Power
        The power the unit belongs to.

    force : Force
        The Force instance of the unit.

    location : Location
        The current location of the unit.

    Attributes
    ----------
    id : integer
        See Parameters.

    owner : Power
        See Parameters.

    force : Force
        See Parameters.

    location : Location
        See Parameters.

    specifiers : list of strings
        A list of the specifiers which may appear in the names
        of locations holding the unit.

    province : Province
        The Province asociated with the current location of the 
        unit. An alias for `self.location.province`

    """

    def __init__(self, id, owner, force, location):
        """ Constructor.

        """
        self.id = id
        self.owner = owner
        self.force = force
        self.location = location

    def __str__(self, suffix='.'):
        """ Print format.

        """
        return (f'{self.owner.genitive} {self.force.name} in '
                f'{self.location.name}{suffix}')

    @property
    def specifiers(self):
        """ specifiers getter.
        
        """
        return self.force.specifiers
    
    @property
    def province(self):
        """ province getter.
        
        """
        return self.location.province

    def move_to(self, location):
        """ Changes the unit's location and province.

        """
        self.location = location

    def sort_string(self):
        """ Returns the string by which units are sorted.
        
        """
        return f'{self.owner}{self.id}'
