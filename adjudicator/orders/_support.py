""" The Support class

"""


from adjudicator.orders.lib import Order


class Support(Order):
    """ A Support is an order for to a unit to aid an 'object unit' in its
    order.

    Attributes:
    name : string
    	class attribute: 'support'
    
        relevance : intger
            The relevance of the move relative other types of orders; sorting
            by relevance gives a faster adjudication process.
        unit : Unit
            The unit the order is given to.
        province : Province
            The current province of the unit.
        object_order : Order
            The order to which support is given.
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

    relevance = 3

    name = 'support'

    def __init__(self, unit, object_order, max_hold=34):
        """ The constructor for the Support class.

        Parameters
        ----------
        unit : Unit
        object_order : Order

        """
        self.unit = unit
        self.object_order = object_order
        self.max_status = 'valid'
        self.min_status = 'illegal'
        self.max_hold = max_hold
        self.min_hold = 1

    def __str__(self):
        """ Method to print a support.

        """
        if not(self.resolved):
            resolution = ' [unresolved]'

        else:
            if self.max_status < 'valid':
                resolution = ' (fails)'
            else:
                resolution = ' (succeeds)'

        return (f"{self.unit.owner.genitive} {self.unit.force} in "
                f"{self.unit.location.name} supports "
                f"{self.object_order.__str__('support')}{resolution}.")

    @property
    def province(self):
        """ province getter.
        
        """
        return self.unit.location.province

    def sort_string(self):
        """ Returns the string format by which units are sorted.
        
        """
        return self.unit.sort_string()

    def __supports_move_on__(self, province):
        """ Method to test whether self supports a move into a province.

        """
        if not self.object_order.name == 'move':
            return False
        return self.object_order.target.province is province

    def __legalize__(self, orders, game_map, verbose=False):
        """ Method to resolve legality of the move.

        """
        relevant = next((order for order in orders
                         if order.unit is self.object_order.unit), None)

        reached = [location.province for location in game_map.locations
                   if location.id in self.unit.location.connections]

        # These two lines should be irrelevant?
        if relevant is None:
            self.max_status = 'illegal'

        elif self.object_order.name == 'hold':
            if relevant.name == 'move':
                self.max_status = 'illegal'
            elif relevant.province in reached:
                self.min_status = 'cut'
            else:
                self.max_status = 'illegal'

        elif self.object_order.name == 'move':
            if verbose:
                print('\tSupporting a move order.')
            if not relevant.name == 'move':
                self.max_status = 'illegal'
            elif relevant.target.province in reached:
                self.min_status = 'cut'
                if verbose:
                    print("\tmin_status increased to 'cut'.")

            else:
                self.max_status = 'illegal'
        else:
            self.max_status = 'illegal'

    def __resolve_attacked__(self, orders, verbose=False):
        """ Method to resolve whether the support is cut.

        """
        targets = [order.target.province for order in orders
                   if order.name == 'move'
                   and order.cutting is True
                   and order.unit.owner != self.unit.owner]

        if self.province in targets:
            self.max_status = 'cut'
            if verbose:
                print("\tUnit is attacked; max_status is 'cut'.")

    def __resolve_left_alone__(self, orders, verbose=False):
        """ Method to resolve whether the support is not cut.

        """
        targets = [order.target.province for order in orders
                   if order.name == 'move'
                   and order.cutting is not False
                   and order.unit.owner != self.unit.owner]

        if not(self.province in targets):
            self.min_status = 'valid'
            if verbose:
                print("\tUnit is left alone; min_status is 'valid'.")

    def resolve(self, variant, orders, verbose=False):
        """ Main method to resolve a support.

        """
        if verbose:
            print(f'Resolving support of unit in {self.unit.province}.')

        if not self.__resolved__('hold'):
            self.__compute_hold_strengths__(orders)

        if self.min_status == 'illegal':
            self.__legalize__(orders, variant.map, verbose)

        if self.min_status > 'illegal':
            self.__resolve_attacked__(orders, verbose)
            self.__resolve_left_alone__(orders, verbose)

    @property
    def resolved(self):
        """

        """
        return self.__resolved__('status') and self.__resolved__('hold')
