""" The RetreatOrders class

"""


from adjudicator.orders.lib import OrderCollection


class RetreatOrders(OrderCollection):
    """ An instance of RetreatOrders is a collection of retreat
    orders for a retreat phase.

    Parameters
    ----------
    retreat : Order type
    	The order type which should be used at initialization.
    
    orders : List of Orders
        The resolved orders of the previous (Diplomacy) phase,
        from which we will deduce the set of units that are
        going to retreat.

    """

    def __init__(self, retreat, orders):
        """ Constructor.
 
        """
        self.orders = []

        for order in orders:

            # We check for units in the target provinces of all successful
            # moves.
 
            if not order.moves():
                continue

            # Warning: Diplomacy phase has been executed, meaning that in case
            # of retreats there is more than one unit in a province.

            object_order = orders.order_in(order.target.province)

            if object_order is None or object_order.moves():
                continue

            # The object_order will be forced to retreat.  There might be some
            # provinces it is not allowed to retreat to, which other units would
            # be allowed to retreat to.
            if order.convoy:
                blocked_for_unit = orders.blocks()

            else:
                blocked_for_unit = orders.blocks() + [order.province]

            self.insert(retreat(0, object_order.unit, blocked_for_unit))
