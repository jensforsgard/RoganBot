""" The OrderCollection class

"""


from adjudicator.lib import flatten
from adjudicator.wrappers import require


class OrderCollection:
    """ An instance is a collection of orders.

    This is a meta class that holds method common for the classes
    BuildOrders, DiplomacyOrders, and RetreatOrders.

    """

    def __init__(self, orders):
        """ Constructor.
 
        """
        self.orders = orders

    def __iter__(self):
        """ Iterator.
        
        """
        for item in self.orders:
            yield item

    def __len__(self):
        """ Length.
        
        """
        return len(self.orders)

    def insert(self, order):
        """ Adds an order to the collection.
        
        """
        if isinstance(order, list):
            self.orders += order
        
        else:
            self.orders.append(order)

    def remove(self, order):
        """ Removes an order from the collection.
        
        """
        self.orders = [entry for entry in self.orders if entry != order]

    def remove_unit(self, unit):
        """ Deletes the order belonging to a specific unit.
        
        """
        self.orders = [entry for entry in self.orders if entry.unit != unit]

    @require
    def order_in(self, province, orders=None):
        """ Retrieves the order of a unit in a province. Throws an error if
        an order is required but not available. You may restrict the search
        to a specific set of orders.

        """
        if orders is None:
            orders = self.orders

        generator = (order for order in orders if order.province is province)
        return next(generator, None)

    @require
    def order_of(self, unit):
        """ Retrieves the order of a given unit. Throws an error if an order 
        is required but not available. You may restrict the search to a 
        specific set of orders.

        """
        generator = (order for order in self if order.unit is unit)
        return next(generator, None)

    def aids(self, order, string, **kwargs):
        """ Retrieves the list of orders of type `string` which are acting
        on the given order.
        
        """
        return [entry for entry in self.orders
                if entry.name == string
                and order.__object_equivalent__(entry.object_order)]

    def all_moves_to(self, province):
        """ Retrieves the `failed` status for all moves form the order
        collection whose target is in the given province.
        
        """
        return [entry.failed for entry in self.orders
                if entry.name == 'move'
                and entry.target.province is province]

    def blocks(self):
        """ Returns the list or provinces which are blocked by a set of
        (resolved) orders.
    
        """
        return list(set(flatten([order.blocks() for order in self])))

    def sort(self, **kwargs):
        """ Sorts the list of orders.

        """
        self.orders.sort(key=lambda order: order.sort_string())
