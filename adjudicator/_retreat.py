""" The Retreat class.

"""

from adjudicator import Disband
from adjudicator._orders import Move

class Retreat:
    """ A Retreat is an order for a unit that was dislodged. 
    The unit can be ordered to move (to an _allowed_ location)
    of to disband.

    Parameters
    ----------
    id : integer
        The id number of the retreat.
    
    unit : Unit
        The unit which was forced to retreat.

    forbidden : list of Provinces
        The list of provinces into which retreats are not allowed.

    Attributes
    ----------
    id : integer
        See Parameters.

    unit : Unit
        See Parameters.

    forbidden : list of Provinces
        See Parameters.

    province : Province
        The province of `self.unit`.

    order : Move or Disband
        The order which is given to the retreating unit.

    legal : boolean
        Whether the given order is legal or not.

    disbands : boolean
        Whether the unit will disband.
    
    resolved : boolean
        Whether the order is resolved.

    Notes
    -----
    The unit might disband either because it was given a disband
    order, or because the given move order failed (for any reason).

    """

    def __init__(self, id, unit, forbidden):
        """ Constructor.

        """
        self.id = id
        self.unit = unit
        self.forbidden = forbidden

        self.order = Disband(0, unit.owner, unit)

        self.legal = None
        self.disbands = None


    def __str__(self):
        """ Print format.

        """
        string = f'The {self.unit.force} in {self.province.name}'

        if isinstance(self.order, Disband):
            return (f'{string} disbands.')
        
        elif self.disbands:
            return (f'{string} retreats to {self.order.target.name} (fails).')

        else:
            return (f'{string} retreats to {self.order.target.name}.')

    @property
    def province(self):
        """ province getter.
        
        """
        return self.unit.location.province

    @property
    def disbands(self):
        """ disbands getter.
        
        """
        return self._disbands
    
    @disbands.setter
    def disbands(self, value):
        """ disbands setter.
        
        """
        try:
            if self._disbands is None:
                self._disbands = value

        except AttributeError:
            self._disbands = value

    @property
    def legal(self):
        """ legal getter.
        
        """
        return self._legal
    
    @legal.setter
    def legal(self, value):
        """ legal setter.
        
        """
        try:
            if self._legal is None:
                self._legal = value

        except AttributeError:
            self._legal = value
 
    @property
    def resolved(self):
        """ resolved getter.
        
        """
        try:
            return (self.legal is not None) and (self.disbands is not None)
    
        except AttributeError:
            return Fase

    def sort_string(self):
        """ Returns the string format by which orders are sorted.
        
        """
        return self.unit.sort_string()

    def resolve(self, variant, orders, verbose=False):
        """ Resolves a retreat order.
        
        Parameters
        ----------
        variant : Variant
            The variant of the game; used when deducing locations the
            unit is not allowed to retreat to.
        
        orders : list of Orders
            The set of all retreat orders for the current retreat phase.
            Used when deducing locations the unit is not allowed to
            retreat to.

        verbose : bool, default=False
            Whether partial progress should be printed. Exists for
            debugging reasons.

        Notes
        -----
        We need to determine both if the order disbands and if it is legal,
        in order to resolve other retreat orders.
        
        The setter functions for `legal` and `disbands` will perform a check
        of whether the order is resolved or not.

        """
        if verbose:
            print(f'\nResolving retreat of {self.unit.location.name}.')
            
        # Disband orders are immediate to resolve.
        if isinstance(self.order, Disband):
            self.legal = True
            self.disbands = True
            return

        # From here, we can assume that `self.order` is a Move order

        # Check that the target location is not forbidden.
        if (not self.legal) and self.order.target.province in self.forbidden:
            self.legal = False
            self.disbands = True
            return

        # Check that the unit can reach the target location
        if (not self.legal) and not self.unit.reaches(self.order.target):
            self.legal = False
            self.disbands = True
            return
        
        self.legal = True

        if verbose:
            print('    Retreat order is legal.')

        # Retrieve the legality of all other retreat orders with the
        # same target province as `self`
        legals = [retreat.legal for retreat in orders
                  if retreat is not self
                  and isinstance(retreat.order, Move)
                  and (retreat.order.target.province 
                       is self.order.target.province)]

        # First case: There is another legal order with same target 
        # province. Then the retreat fails.
        if True in legals:
            self.disbands = True
            return

        # Second case: All other orders with same province are illegal,
        # then the retreat succeeds.
        if None not in legals:
            self.disbands = False
            return
        
        # Third case: There is at least one order with the same target
        # province, whose legality is yet to be determined. We cannot
        # draw any further conclusions at this point.
        return
