""" The DiplomacyOrders class

"""


from adjudicator.orders.lib import OrderCollection


class DiplomacyOrders(OrderCollection):
    """ An instance of DiplomacyOrders is a collection of orders
    for a diplomacy phase.

    Parameters
    ----------
	hold : Order subclass
		The order type which should be given at initialization.

    units : List of Units, default=[]
        The units appearing in the game for the current diplomacy phase.

    Attributes
    ----------
    orders : List of Orders
        The list of orders of the units appearing in the current phase.

    """

    def __init__(self, hold, units=[]):
        """ Constructor.
 
        """
        self.orders = [hold(unit) for unit in units]

    def sort(self, by='normal'):
        """ Sorts the list of orders.

        """
        if by == 'relevance':
            self.orders.sort(key=lambda order: order.relevance)
        else:
            self.orders.sort(key=lambda order: order.sort_string())