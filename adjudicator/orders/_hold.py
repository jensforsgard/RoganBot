""" The Hold class

"""


from adjudicator.orders.lib import Order


class Hold(Order):
    """ A Hold is an order for to a unit to remain in its place.

    Attributes:
    name : string
    	class attribute: 'hold'
    
        relevance : intger
            The relevance of the move relative other types of orders; sorting
            by relevance gives a faster adjudication process.
        unit : Unit
            The unit the order is given to.
        province : Province
            The current province of the unit.
        statuses : dictionary
            Dictionary of statuses and their ordering.
        max_status : string
            The maximal status of the move as currently known.
        min_status : string
            The minimal status of the move as currently known.
        max_hold : integer
            The maximal hold strength of the unit.
        min_hold : integer
            The minimal hold strength of the unit.
        resolved : boolean or None
            Whether the move is resolved or not.

    """

    relevance = 4

    name = 'hold'

    def __init__(self, unit):
        """ The constructor for the Hold class.

        Parameters
        ----------
        unit : Unit

        """
        self.unit = unit
        self.province = unit.location.province
        self.max_status = 'valid'
        self.min_status = 'illegal'
        self.resolved = False
        self.max_hold = 34
        self.min_hold = 1

    def __str__(self, context='self'):
        """  Method to print a hold order.

        """
        if not self.resolved and context == 'self':
            resolution = ' [unresolved]'
        else:
            resolution = ''
        if context == 'support':
            prefix = 'the'
            suffix = ''
        else:
            prefix = self.unit.owner.genitive
            suffix = '.'
        return (f'{prefix} {self.unit.force} in '
                f'{self.unit.location.name} holds{resolution}{suffix}')

    def sort_string(self):
        """ Returns the string format by which units are sorted.
        
        """
        return self.unit.sort_string()

    def resolve(self, variant, orders, verbose=False):
        """ Method to resolve status.

        """
        self.min_status = 'valid'
        if not self.__resolved__('hold'):
            self.__compute_hold_strengths__(orders)
        if self.__resolved__('hold'):
            self.resolved = True
        # else: Status could not be resolved at this time.

