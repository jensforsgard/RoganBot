""" The Support class

"""


from yaml import load, Loader

from adjudicator.orders.lib import Order


with open('adjudicator/config.yaml', 'r') as file:
    RELEVANCE = load(file, Loader)['relevance']


class Support(Order):
    """ A Support is an order for to a unit to aid an 
    `object unit` in their order.

    Parameters
    ----------
    unit : Unit
        The unit the order is given to.
    
    object_order : Order
        The order which is supported

    max_hold : integer
        The maximum hold strength.

    Attributes:
    -----------
    name : string
        class attribute: 'support'
    
    relevance : intger
        The relevance of the move relative other types of orders;
        sorting by relevance gives a faster adjudication process.
    
    unit : Unit
        See Parameters.

    province : Province
        The current province of the unit.

    object_order : Order
        The order to which support is given.

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

    relevance = RELEVANCE['support']

    name = 'support'

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
        """ Method to print a support.

        """
        if not(self.resolved):
            resolution = ' [unresolved]'

        elif self.max_status < 'valid':
            resolution = ' (fails)'
        
        else:
            resolution = ' (succeeds)'

        return (f"{self.unit.owner.genitive} {self.unit.force} in "
                f"{self.unit.location} supports "
                f"{self.object_order.__str__('support')}{resolution}.")

    def __supports_move_on__(self, province):
        """ Method to test whether self supports a move into a province.

        """
        try:
            return self.object_order.target.province is province
        
        except AttributeError:
            return False

    def __legalize__(self, orders, game_map):
        """ Method to resolve the legality of the support order.

        """
        # The `relevant` order is the order of the unit being supported
        relevant = orders.order_of(self.object_order.unit)

        reached = [game_map.locations[k].province 
                   for k in self.unit.location.connections]

        # If the object order is a hold, then the support is legal
        # as long as the `relevant` order is not a move.
        if self.object_order.name == 'hold':

            if (relevant.province in reached) and (relevant.name != 'move'):
                self.min_status = 'cut'

            else:
                self.max_status = 'illegal'

        # If the object order is a move, then the support is legal only
        # if the `relevant` order is a move into the same province.
        elif self.object_order.name == 'move':

            if (relevant.name == 'move') and (relevant.target.province in reached):
                self.min_status = 'cut'

            else:
                self.max_status = 'illegal'
        
        # It is possible to, formally, support convoys and supports,
        # but such orders are not legal.
        else:

            self.max_status = 'illegal'

    def __resolve_attacked__(self, orders):
        """ Method to resolve whether the support is cut.

        """
        relevant = orders.all_moves_to(
            self.province,
            attr='cutting',
            exclude_power=self.unit.owner
        )

        # If attacked, reduce max_status
        if True in relevant:
            self.max_status = 'cut'

        # If not attacked, increase min_status
        elif None not in relevant:
            self.min_status = 'valid'

    def resolve(self, variant, orders):
        """ Main method to resolve a support.

        """
        if not self.__resolved__('hold'):
            self.__compute_hold_strengths__(orders)

        if self.min_status == 'illegal':
            self.__legalize__(orders, variant.map)

        if self.min_status > 'illegal':
            self.__resolve_attacked__(orders)
