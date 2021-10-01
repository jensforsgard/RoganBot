""" The Order class

"""


from adjudicator.orders.lib import OrderStatus


class Order:
    """ Order is a meta class that holds the methods common to all
    orders given during the diplomacy phase.
    
    See: `adjudicator.Convoy`, `adjudicator.Hold`, `adjudicator.Move`
    and `adjudicator.Support`.
    
    Attributes
    ----------
    min_status : OrderStatus
        The minimum status of the order, as currently deduced.
    
    max_status : OrderStatus
        The maximum status of the order, as currently deduced.
    
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
            if self._max_status < value:
                self._min_status = self._max_status

            elif self._min_status < value:
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
            if self._min_status > value:
                self._max_status = self.min_status

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

    def __resolved__(self, attr):
        """ Method to test if an attribute is resolved.

        """
        return getattr(self, f'max_{attr}') == getattr(self, f'min_{attr}')

    def __compute_hold_strengths__(self, orders):
        """  Method to compute hold strengths.

        """
        if not self.__resolved__('hold'):
            supports = orders.aids(self, 'support')
            
            possible = [order for order in supports if order.max_status == 'valid']
            known = [order for order in supports if order.min_status == 'valid']
    
            self.max_hold = 1 + len(possible)
            self.min_hold = 1 + len(known)

    def moves(self):
        """ Method to check whether the order is a successful move.

        The class :cls:adjudicator.Move overrides this method.
    
        """
        return False

    def blocks(self):
        """ Method to retrieve the provinces blocked by the unit during the
        retreat phase.

        The class :cls:adjudicator.Move overrides this method.

        """
        return [self.province]

    def __object_equivalent__(self, order):
        """ Method to check whether the instance is equivalent to an order
        as objects of other orders.

        The class :cls:adjudicator.Move overrides this method.

        """
        return (order.province is self.province
                and not self.name == 'move'
                and not order.name == 'move')
