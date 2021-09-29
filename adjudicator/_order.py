""" The Order class

"""

from adjudicator.lib import flatten
from lib.classes import orders_of_type

from adjudicator.orders import OrderStatus

from yaml import load, Loader

with open('adjudicator/config.yaml', 'r') as file:
    RELEVANCE = load(file, Loader)['relevance']

class Order:
    """ Order is a meta class that holds the methods common to all
    orders given during the diplomacy phase.

    """

    @property
    def min_status(self):
        """ min_status getter.
        
        """
        return self._min_status

    @min_status.setter
    def min_status(self, value):
        """ min_status setter.
        
        """
        try:
            if self._min_status < value:
                self._min_status.set(value)
        
        except AttributeError:
            self._min_status = OrderStatus(value)

    @min_status.deleter
    def min_status(self):
        """ min_status deleter.
        
        """
        del self._min_status

    @property
    def max_status(self):
        """ max_status getter.
        
        """
        return self._max_status

    @max_status.setter
    def max_status(self, value):
        """ max_status setter.
        
        """
        try:
            if self._max_status > value:
                self._max_status.set(value)
        
        except AttributeError:
            self._max_status = OrderStatus(value)

    @max_status.deleter
    def max_status(self):
        """ min_status deleter.
        
        """
        del self._max_status

    def reset(self, max_hold=34):
        """ Method to reset an order.

        """
        del self.max_status, self.min_status

        self.max_status = 'valid'
        self.min_status = 'illegal'
        self.max_hold = max_hold
        self.min_hold = 1

    def set_(self, attr, value):
        """ Method to set an attribute value without overwriting a possible
        earlier assigned value.

        """
        if getattr(self, attr) is None:
            setattr(self, attr, value)

    def is_type(self, string):
        """
        
        """
        return self.relevance == RELEVANCE[string]

    def moves(self):
        """ Method to check whether the order is a successful move.

        """
        return (self.is_type('move') and self.min_status == 'valid' 
                and not self.failed)

    def __resolved__(self, attr):
        """ Method to test if an attribute is resolved.

        """
        return getattr(self, f'max_{attr}') == getattr(self, f'min_{attr}')

    def __object_equivalent__(self, order):
        """ Method to check whether the instance is equivalent to an order
        as objects of other orders.

        """
        if self.is_type('move'):
            return (order.is_type('move')
                    and order.province is self.province
                    and order.target.province is self.target.province)
        else:
            return order.is_type('hold') and order.province is self.province

    def __object_of__(self, orders, order_class):
        """ Method to retrieve the orders of a certain class of which self is
        the object order.

        """
        assert order_class in ['support', 'convoy']
        # Since supports are given to provinces rather than locations,
        # we can't just compare the object_order with self.
        orders = orders_of_type(orders, order_class)
        return [order for order in orders
                if self.__object_equivalent__(order.object_order)]

    def __compute_hold_strengths__(self, orders):
        """  Method to compute hold strengths.

        """
        # The first check prevents hold strength for Move orders to be changed
        # from their static value = 1.
        if self.__resolved__('hold'):
            return
        supports = self.__object_of__(orders, 'support')
        possible = [order for order in supports if order.max_status == 'valid']
        known = [order for order in supports if order.min_status == 'valid']
        self.max_hold = 1 + len(possible)
        self.min_hold = 1 + len(known)

    def blocks(self):
        """ Method to retrieve the provinces blocked by the unit during the
        retreat phase.

        """
        return [self.province]
