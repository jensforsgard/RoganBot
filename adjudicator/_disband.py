""" The Disband class

"""

from random import choice

class Disband:
    """ A Disband is an order to remove a unit from the game.

    Parameters
    ----------
    id : integer
        The id number of the order.

    owner : Power
        The power which the order belongs to.
    
    unit : Unit
        The unit which is should be removed.

    Attributes
    ----------
    id : integer
        See Parameters.

    unit : Unit
        See Parameters.

    owner : Power
        See Parameters.

    province : Province
        The province containing the unit to be removed.

    resolved : boolean
        Whether the order is resolved or not.

    """

    def __init__(self, id, owner, unit=None):
        """ Constructor.

        """
        self.id = id
        self.owner = owner
        self.unit = unit
        self.resolved = False

    def __str__(self):
        """ Method to print a disband.

        """
        try:
            string = f'{self.unit.force} in {self.province.name}.'
        
        except AttributeError:
            string = 'by default.'

        return f'{self.owner.genitive} disband no. {self.id} is {string}'

    @property
    def province(self):
        """ province getter.
        
        """
        try:
            return self._unit.location.province
        
        except AttributeError:
            return None

    def sort_string(self):
        """ Returns the string format by which units are sorted.
        
        """
        return f'{self.owner}{self.id}'

    def postpone(self):
        """ Sets as a postponed order.
        
        """
        self.unit = None

    @property
    def unit(self):
        """ _unit getter.
        
        """
        return self._unit

    @unit.setter
    def unit(self, unit):
        """ Sets the unit to disband.
        
        """
        try:
            assert unit.owner is self.owner
            self._unit = unit
        
        except AttributeError:
            self._unit = None

    def invalid_action(self, units, orders):
        """ The action to take if the order is invalid.
        
        This is where there should be an algorithm implemented for how
        to choose a unit to disband, if no appropriate disband order was
        given. At the moment, since this is irrelevant for the purposes
        of this adjudicator, a random choice is made.

        """
        if self.unit is None:
        
            # Existing units that have been ordered to disbans
            gone = [order.unit for order in orders
                    if isinstance(order, Disband)
                    and order.unit is not None]
            
            # Units belonging to `self.owner` that has not already
            # been ordered to disband.
            available = [unit for unit in units
                         if unit not in gone
                         and unit.owner is self.owner]

            # Make a choice.
            self.unit = choice(available)
