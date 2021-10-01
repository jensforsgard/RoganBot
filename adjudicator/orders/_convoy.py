""" The Convoy class

"""

from yaml import load, Loader

from adjudicator.orders.lib import Order


with open('adjudicator/config.yaml', 'r') as file:
    RELEVANCE = load(file, Loader)['relevance']


class Convoy(Order):
    """ A Convoy is an order for a Fleet to aid an army in moving
    across water.

    Parameters
    ----------
    unit : Unit
        The unit the order is given to.
    
    object_order : Order
        The move order that the fleet is trying to aid in.

    Attributes
    ----------
    name : string
        class attribute: 'convoy'
    
    unit : Unit
        See Parameters.
    
    object_order : Order
        See Parameters.
    
    relevance : integer
        The relevance of the order relative other types of orders;
        sorting by relevance gives a faster adjudication process.
        Class attribute.
    
    province : Province
        The current province of the unit.

    statuses : dictionary
        Dictionary of possible statuses and their ordering.
        Class attribute.

    max_status : OrderStatus
        The maximal status of the move as currently known.
    
    min_status : OrderStatus
        The minimal status of the move as currently known.
    
    max_hold : integer
        The maximal hold strength of the unit.
    
    min_hold : integer
        The minimal hold strength of the unit.
    
    resolved : boolean
        Whether the move is resolved or not.

    Notes
    -----
    The status of the order depends on the other order in the game for
    the given turn and might, at any given moment, be unknown.

    """

    relevance = RELEVANCE['convoy']

    name = 'convoy'

    def __init__(self, unit, object_order, max_hold=34):
        """ Constructor.

        """
        self.unit = unit
        self.object_order = object_order

        self.max_status = 'valid'
        self.min_status = 'illegal'

        self.max_hold = max_hold
        self.min_hold = 1

    def __str__(self):
        """ Method to print a convoy.

        """
        if not(self.resolved):
            resolution = '[unresolved]'

        elif self.min_status == 'valid':
            resolution = '(succeeds)'
        
        else:
            resolution = '(fails)'

        return (f"{self.unit.owner.genitive} {self.unit.force} in "
                f"{self.province} convoys "
                f"{self.object_order.__str__('convoy')} {resolution}.")



    def __legalize__(self, orders):
        """ Method to resolve the legality of a convoy.

        """
        convoyed = orders.order_of(self.object_order.unit)

        if convoyed is None or convoyed.unit.force.name == 'Fleet':
            self.max_status = 'illegal'

        elif not convoyed.name == 'move':
            self.max_status = 'illegal'

        elif convoyed.target is not self.object_order.target:
            self.max_status = 'illegal'

        else:
            self.min_status = 'broken'

    def resolve_dislodged(self, orders, verbose=False):
        """ Method to resolve dislodgement of a convoying fleet.

        """
        if self.min_status < 'valid':
            results = [order.failed for order in orders
                       if order.name == 'move'
                       and order.target.province is self.province]

            return None if (None in results) else (False in results)

    def resolve(self, variant, orders, verbose=False):
        """ Main method to resolve a convoy order.

        """
        if not self.max_hold == self.min_hold:
            self.__compute_hold_strengths__(orders)

        if self.min_status == 'illegal':
            self.__legalize__(orders)

        if self.min_status > 'illegal':

            # dislodged can be True, False, or None. If the value is None,
            # then whether the fleet is dislodged or not depends on other
            # orders which are not yet resolved.
            dislodged = self.resolve_dislodged(orders)

            if dislodged is True:
                self.max_status = 'broken'

            elif dislodged is False:
                self.min_status = 'valid'
