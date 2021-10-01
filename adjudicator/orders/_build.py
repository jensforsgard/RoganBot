""" The Build class

"""

class Build:
    """ A Build is an order to add a new unit to the game.

    Parameters
    ----------
    id : integer
        The id number; should be unique for the given power.
    
    owner : Power
        The Power which the build belongs to.

    force : Force or None, default=None
        The force of the unit being built. `None` if the build
        order is postponed.

    location : Location or None, default=None
        The location where the unit should be built. `None` if
        the build order is postponed.

    Attributes
    ----------
    name : string
        class attribute: 'build'
    
    id : integer
        See Parameters.
    
    owner : Power
        See Parameters.

    force : Force or None
        See Parameters.

    location : Location or None
        See Parameters.

    province : Province or None
        The province associated with the location of the build,
        and `None` if the build is postponed. An alias for
        `location.province`. 

    failed : bool
        Whether the order is legal or not.
    
    resolved : bool
        Whether the order is resolved.

    """

    name = 'build'

    def __init__(self, id, owner, force=None, location=None):
        """ Constructor.

        """
        self.id = id
        self.owner = owner
        
        self.force = force
        self.location = location

        self.resolved = False

    def __str__(self):
        """ Print format.

        """
        try:
            string = f'{self.force.name} in {self.location.name}.'
        
        except AttributeError:
            string = 'postponed.'

        return f'{self.owner.genitive} build no. {self.id} is {string}'

    def sort_string(self):
        """ Returns the string format by which units are sorted.
        
        """
        return f'{self.owner}{self.id}'
    
    @property
    def province(self):
        """ province getter.
        
        """
        try:
            return self.location.province
        
        except AttributeError:
            return None

    def postpone(self):
        """ Sets as a postponed order.
        
        """
        self.force = None
        self.location = None

    def invalid_action(self, *args):
        """ The action to take if the order is invalid. For build order,
        it means the build is postponed.

        This method only exists to provide consistency between the
        Build and Disband classes.

        """
        self.postpone()
