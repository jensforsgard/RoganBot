""" The Hold class

"""


from yaml import load, Loader

from adjudicator.orders.lib import Order


with open('adjudicator/config.yaml', 'r') as file:
    RELEVANCE = load(file, Loader)['relevance']


class Hold(Order):
    """ A Hold is an order for to a unit to remain in its place.

    Parameters
    ----------
    unit : Unit
        The unit being ordered to hold.

    max_hold : integer, default=34
        The maximum hold strength. Depends on the map.

    Attributes
    ----------
    name : string
        class attribute: 'hold'
    
    relevance : integer
        The relevance of the hold order relative other orders.

    unit : Unit
        See Parameters.

    province : Province
        The current province of the unit.
    
    max_status : OrderStatus
        The maximal status of the move, as currently known.
    
    min_status : OrderStatus
        The minimal status of the move, as currently known.
    
    max_hold : integer
        The maximal hold strength of the unit, as currently known.
    
    min_hold : integer
        The minimal hold strength of the unit, as currently known.
    
    resolved : boolean or None
        Whether the move is resolved or not.

    """

    relevance = RELEVANCE['hold']

    name = 'hold'

    def __init__(self, unit, max_hold=34):
        """ Constructor

        """
        self.unit = unit
        self.max_status = 'valid'
        self.min_status = 'illegal'
        self.max_hold = max_hold
        self.min_hold = 1

        self.province = unit.location.province

    def __str__(self, context='self'):
        """  Method to print a hold order.

        """
        if context == 'self':
            return ''.join([
                f'{self.unit.owner.genitive} {self.unit.force} ',
                f'in {self.unit.location} holds',
                ('.' if self.resolved else ' [unresolved].')
            ])
        
        else:
            return f'the {self.unit.force} in {self.unit.location} holds'

    def sort_string(self):
        """ Returns the string format by which units are sorted.
        An alias for `self.unit.sort_string`.
        
        """
        return self.unit.sort_string()

    @property
    def resolved(self):
        """ resolved getter.
        
        """
        return self.__resolved__('status') and self.__resolved__('hold')

    def resolve(self, variant, orders, verbose=False):
        """ Method to resolve status.

        """
        # Hold orders are always valid.
        self.min_status = 'valid'

		# Resolve hold strength.
        if not self.__resolved__('hold'):
            self.__compute_hold_strengths__(orders)
