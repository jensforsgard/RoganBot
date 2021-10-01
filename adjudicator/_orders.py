#!/usr/bin/env python3# -*- coding:utf-8 -*-""" This module contains order classes."""from adjudicator.lib import flattenfrom adjudicator.orders import Order, OrderStatusfrom adjudicator import Disbandclass Move(Order):    """ A Move is an order for to a unit to change its location.    Attributes:        relevance : intger            The relevance of the move relative other types of orders; sorting            by relevance gives a faster adjudication process.        unit : Unit            The unit the order is given to.        province : Province            The current province of the unit.        target : Location            The target location of the move.        convoy : boolean            Whether the move is via convoy or not.        statuses : dictionary            Dictionary of statuses and their ordering.        max_status : string            The maximal status of the move as currently known.        min_status : string            The minimal status of the move as currently known.        max_hold : integer            The maximal hold strength of the unit.        min_hold : integer            The minimal hold strength of the unit.        max_move : dictionary            A dictionary of maximal move strengths when including all supports            or exluding supports of certain powers.        min_move : dictionary            A dictionary of minimal move strengths when including all supports            or exluding supports of certain powers.        cutting : boolean or None            Whether the move cuts support or not.        dislodging : boolean or None            Whether the move may dislodge a unit.        failed : boolean or None            Whether the move fails or not.        resolved : boolean or None            Whether the move is resolved or not.    """    relevance = 2    max_hold = 1    min_hold = 1    def __init__(self, unit, convoy, target):        """ The constructor for the Move class.        Parameters        ----------        unit : Unit        convoy : boolean        target : Location        """        self.unit = unit        self.province = unit.location.province        self.convoy = convoy        self.target = target        self.max_status = 'valid'        self.min_status = 'illegal'        self.cutting = None        self.dislodging = None        self.failed = None        self.resolved = False        self.max_move = {None: 34}        self.min_move = {None: 1}    def __str__(self, context='self'):        """ Print method.        """        routes = {False: 'move', True: 'move via convoy'}        resolutions = {True: '(fails)', False: '(succeeds)',                       None: '[unresolved]'}        if context == 'self':            return (f'{self.unit.__str__("")} {routes[(self.convoy)]} to '                    f'{self.target.name} {resolutions[self.failed]}.')        elif context == 'support':            return (f'the move {self.unit.location.name} to '                    f'{self.target.province.name}')        elif context == 'convoy':            return f'{self.unit.location.name} to {self.target.name}'    def sort_string(self):        """ Returns the string format by which units are sorted.                """        return self.unit.sort_string()    def reset(self):        """ Reset to the initial attribute values.        """        del self.max_status, self.min_status        self.max_status = 'valid'        self.min_status = 'illegal'        self.cutting = None        self.dislodging = None        self.failed = None        self.resolved = False        self.max_move = {None: 34}        self.min_move = {None: 1}    def set_illegal(self):        """ Method to set a move to illegal.        """        self.max_status = 'illegal'        self.set_('cutting', False)        self.set_('dislodging', False)        self.set_('failed', True)        for entry in self.min_move.keys():            self.min_move[entry] = 0        for entry in self.max_move.keys():            self.max_move[entry] = 0        self.set_resolved()    def set_resolved(self, verbose=False):        """ Method to set a move to resolved.        """        param = None not in [self.cutting, self.dislodging, self.failed]        if (self.__resolved__('status') and self.__resolved__('move')             and param):            self.resolved = True            if verbose and self.failed:                print(f'\tMove is {self.max_status} and/but fails.')            elif verbose and not self.failed:                print(f'\tMove succeeds.')                def __adjacent_convoy__(self, orders):        """ Method to employ a rule variation for adjacent convoys.                """        # webDip Convoy Rule, light version        adjacent_convoys = [order for order in orders.aids(self, 'convoy')                            if order.unit.location.reaches_province(self.unit.province)]        if self.convoy and (len(adjacent_convoys) == 0):            self.convoy = False            def __object_equivalent__(self, order):        """ Method to check whether the instance is equivalent to an order        as objects of other orders.        """        return (isinstance(order, Move)                and order.province is self.province                and order.target.province is self.target.province)    def __compute_move_strengths__(self, powers, orders):        """ Method to compute move strength, and the modified move strengths        when supports of a certain power are discounted.        Parameters        ----------        powers : list of Powers        orders : list of Orders            The list of order from which we should retrieve support orders.        """        supports = orders.aids(self, 'support')        # We need to keep track of the powers giving the supports, to be        # able to compute the adjusted move strengths.        possible = [order.unit.owner for order in supports                    if order.max_status == 'valid']        known = [order.unit.owner for order in supports                 if order.min_status == 'valid']        self.max_move[None] = 1 + len(possible)        self.min_move[None] = 1 + len(known)        # Computing the adjusted move strengths.        for power in powers:            self.max_move[power] = self.max_move[None] - possible.count(power)            self.min_move[power] = self.min_move[None] - known.count(power)    def moves(self):        """ Method to check whether the move will take place.                """        return self.min_status == 'valid' and not self.failed    def __convoy__(self, map_, orders, attr):        """ Method to check whether a convoy route exists.        """        locations = [order.unit.location for order in orders.aids(self, 'convoy')                     if getattr(order, attr) == 'valid']        return map_.has_path(self.province, self.target.province, locations)    def __repels__(self, order):        """ Method to check whether an order is a move away from the target        province of self.        """        if order is None or not isinstance(order, Move):            return False        elif (self.convoy or order.convoy              or order.target.province is not self.unit.province):            return True        else:            return False    def __opposed_by__(self, order):        """ Method to check whether an order is a move head-to-head with self.        """        if (not isinstance(order, Move)            or self.convoy            or order.convoy            or order.target.province is not self.province            or order.max_status == 'illegal'):            return False        else:            return True    def blocks(self):        """ Method to retrieve the provinces blocked by self during the        retreat phase. Returns a list of provinces.        """        if self.max_status < 'valid':            return [self.province]        elif not self.failed:            return [self.target.province]        else:            return [self.province, self.target.province]    def __supports_attack_on_self__(self, order):        """ Method to check whether an order supports an attack on the source        province of self.        """        return (isinstance(order, Support)                and order.__supports_move_on__(self.province))    def __stronger_than__(self, orders, except_power):        """ Method to check whether the move is the strongest move order        amongst a set of orders, discounting support by except_power.        Parameters:        -----------        orders : list of Moves        except_power : Power        """        if len(orders) == 0:            return True        opponent = max([order.max_move[None] for order in orders])        return self.min_move[except_power] > opponent    def __weaker_than__(self, orders, except_power):        """ Method to check whether the move is weaker (or equal in strength)        than some move order amongst a set of orders, discounting possible        support by except_power.        Parameters        ----------        orders : list of Moves        except_power : Power        """        if len(orders) == 0:            return False        opponent = max([order.min_move[None] for order in orders])        return self.max_move[except_power] <= opponent    def __stronger_attack__(self, order, except_power):        """ Method to check whether the move is stronger than the hold        strength of the unit of an order.        """        return self.min_move[except_power] > order.max_hold    def __weaker_attack__(self, order, except_power):        """ Method to check whether the move is weaker (or eaqual in strength)        to the hold strength of the unit of an order.        """        return self.max_move[except_power] <= order.min_hold    def __bounces__(self, orders, except_entry=None, verbose=False):        """ Method to check whether the move is bounced by other moves,        discounting the support of except_power.        """        try:            except_power = except_entry.unit.owner        except (AttributeError):            except_power = None        possible = [order for order in orders if isinstance(order, Move)                    and order.target.province is self.target.province                    and order is not self                    and order.max_status == 'valid']        known = [order for order in possible if order.min_status == 'valid']        if self.__stronger_than__(possible, except_power):            if verbose:                print('\tMove is not bounced by other attacker.')            return False        if self.__weaker_than__(known, except_power):            if verbose:                print('\tMove is bounced by other attacker.')            return True        if verbose:            print('\tCould not decide if move is bounced by other attacker.')        return None  # Encoding that the bounce remains unresolved    def __attacks__(self, orders, attacked):        """ Method to check whether the attack is successful in dislodging        the defending unit.        """        if attacked.unit.owner == self.unit.owner:            return False        if self.__stronger_attack__(attacked, attacked.unit.owner):            return True        if self.__weaker_attack__(attacked, attacked.unit.owner):            return False        return None  # Encoding that the attack remains unresolved    def __resolve_legality__(self, game_map, orders):        """ Method to resolve the legality of a move order.        """        if not self.convoy:            if self.unit.location.reaches_location(self.target):                self.min_status = 'no effect'            else:                self.set_illegal()        else:            if self.__convoy__(game_map, orders, 'min_status'):                self.min_status = 'valid'            elif not self.__convoy__(game_map, orders, 'max_status'):                self.set_illegal()            # If neither, then legality cannot yet be determined.    def __resolve_hth__(self, attacked, except_=None):        """ Method to resolve the outcome of a head to head battle.        """        if attacked.min_status == 'illegal':            # Cannot resolve if opponent has not been deemed a legal order.            return None        if attacked.unit.owner == self.unit.owner:            return False        elif self.__stronger_than__([attacked], except_):            return True        elif self.__weaker_than__([attacked], except_):            return False        else:            return None    def resolve(self, variant, orders, verbose=False):        """ Main method to resolve a move order.        """        if verbose:            print(f'\nResolving move of unit in {self.unit.location.name}.')        assert not self.resolved, 'Resolve method called for resolved order.'        if self.min_status == 'illegal':            self.__resolve_legality__(variant.map, orders)            if verbose and self.min_status > 'illegal':                print('\tOrder is legal.')        if self.min_status > 'illegal':            if not self.__resolved__('move'):                self.__compute_move_strengths__(variant.powers, orders)                if verbose:                    print(f'\tMax strengths: {list(self.max_move.values())}')                    print(f'\tMin strengths: {list(self.min_move.values())}')                            attacked = next((order for order in orders                             if order.province is self.target.province), None)            if attacked is None:                self.__resolve_empty__(orders, attacked, verbose)            elif self.__repels__(attacked):                self.__resolve_repels____(orders, attacked, verbose)            elif self.__opposed_by__(attacked):                self.__resolve_opposed__(orders, attacked, verbose)            elif self.__supports_attack_on_self__(attacked):                self.__resolve_support_on_self__(orders, attacked, verbose)            else:                self.__resolve_attack__(orders, attacked)            self.set_resolved(verbose)    def __resolve_empty__(self, orders, attacked_order, verbose=False):        """ Method to resolve a move into an empty or emptied province.        """        self.min_status = 'valid'        bounced = self.__bounces__(orders, None)        self.set_('cutting', False)  # Doesn't matter, nothing to cut        self.set_('dislodging', False)  # Doesn't matter, nothing to dislodge        self.set_('failed', bounced)    def __resolve_repels____(self, orders, attacked_order, verbose=False):        """ Method to resolve a move into possibly emptied province. Even if        the move of the unit in the target province is not resolved, we might        still be able to resolve bounces, etc.        """        if verbose:            print('\tResolving an move on a unit moving away.')        self.min_status = 'valid'        self.set_('cutting', False)        if attacked_order.failed is False:            self.__resolve_empty__(orders, attacked_order, verbose)        elif attacked_order.failed is True:            self.__resolve_attack__(orders, attacked_order, verbose)        elif self.__bounces__(orders, None):            self.set_('dislodging', False)            self.set_('failed', True)    def __resolve_opposed__(self, orders, attacked, verbose=False):        """ Method to resolve a head-to-head battle.        """        if verbose:            print('\tResolving an opposed move.')        self.set_('cutting', False)        bounced = self.__bounces__(orders, attacked, verbose=verbose)        win_hth = self.__resolve_hth__(attacked)        mod_hth = self.__resolve_hth__(attacked, attacked.unit.owner)        if attacked.min_status == 'illegal':            pass        elif attacked.failed is False:            self.max_status = 'no effect'            self.set_('dislodging', False)            self.set_('failed', True)        elif attacked.failed is True:            self.min_status = 'valid'            if (bounced is not None) and (mod_hth is not None):                self.set_('dislodging', (not bounced) and mod_hth)                self.set_('failed', bounced or not mod_hth)        elif win_hth is True:            self.min_status = 'valid'            if bounced is not None and mod_hth is not None:                self.set_('dislodging', not bounced and mod_hth)                self.set_('failed', bounced or not mod_hth)        elif win_hth is False:            # Status will depend on whether opposing order bounces.            self.set_('dislodging', False)            self.set_('failed', True)    def __resolve_support_on_self__(self, orders, attacked_order,                                    verbose=False):        """ Method to resolve a move onto a unit supporting an attack on the        source province.        """        self.min_status = 'valid'        if self.dislodging is False:  # Safety measure            self.set_('cutting', False)            self.set_('failed', True)        attack = self.__attacks__(orders, attacked_order)        bounced = self.__bounces__(orders, attacked_order, verbose)        if bounced is None or attack is None:            return None        self.set_('cutting', not bounced and attack)        self.set_('dislodging', not bounced and attack)        self.set_('failed', bounced or not attack)    def __resolve_attack__(self, orders, attacked_order, verbose=False):        """ Method to resolve a move into a privince with a defending unit.        """        if verbose:            print('\tResolving an attack on a unit.')        self.min_status = 'valid'        self.set_('cutting', True)        if self.dislodging is False:            self.set_('failed', True)        attack = self.__attacks__(orders, attacked_order)        bounced = self.__bounces__(orders, attacked_order, verbose)        if bounced is None or attack is None:            return None        self.set_('dislodging', not bounced and attack)        self.set_('failed', bounced or not attack)class Hold(Order):    """ A Hold is an order for to a unit to remain in its place.    Attributes:        relevance : intger            The relevance of the move relative other types of orders; sorting            by relevance gives a faster adjudication process.        unit : Unit            The unit the order is given to.        province : Province            The current province of the unit.        statuses : dictionary            Dictionary of statuses and their ordering.        max_status : string            The maximal status of the move as currently known.        min_status : string            The minimal status of the move as currently known.        max_hold : integer            The maximal hold strength of the unit.        min_hold : integer            The minimal hold strength of the unit.        resolved : boolean or None            Whether the move is resolved or not.    """    relevance = 4    def __init__(self, unit):        """ The constructor for the Hold class.        Parameters        ----------        unit : Unit        """        self.unit = unit        self.province = unit.location.province        self.max_status = 'valid'        self.min_status = 'illegal'        self.resolved = False        self.max_hold = 34        self.min_hold = 1    def __str__(self, context='self'):        """  Method to print a hold order.        """        if not self.resolved and context == 'self':            resolution = ' [unresolved]'        else:            resolution = ''        if context == 'support':            prefix = 'the'            suffix = ''        else:            prefix = self.unit.owner.genitive            suffix = '.'        return (f'{prefix} {self.unit.force} in '                f'{self.unit.location.name} holds{resolution}{suffix}')    def sort_string(self):        """ Returns the string format by which units are sorted.                """        return self.unit.sort_string()    def resolve(self, variant, orders, verbose=False):        """ Method to resolve status.        """        self.min_status = 'valid'        if not self.__resolved__('hold'):            self.__compute_hold_strengths__(orders)        if self.__resolved__('hold'):            self.resolved = True        # else: Status could not be resolved at this time.class Support(Order):    """ A Support is an order for to a unit to aid an 'object unit' in its    order.    Attributes:        relevance : intger            The relevance of the move relative other types of orders; sorting            by relevance gives a faster adjudication process.        unit : Unit            The unit the order is given to.        province : Province            The current province of the unit.        object_order : Order            The order to which support is given.        statuses : dictionary            Dictionary of statuses and their ordering.        max_status : string            The maximal status of the move as currently known.        min_status : string            The minimal status of the move as currently known.        max_hold : integer            The maximal hold strength of the unit.        min_hold : integer            The minimal hold strength of the unit.        resolved : boolean or None            Whether the move is resolved or not.    """    relevance = 3    def __init__(self, unit, object_order, max_hold=34):        """ The constructor for the Support class.        Parameters        ----------        unit : Unit        object_order : Order        """        self.unit = unit        self.object_order = object_order        self.max_status = 'valid'        self.min_status = 'illegal'        self.max_hold = max_hold        self.min_hold = 1    def __str__(self):        """ Method to print a support.        """        if not(self.resolved):            resolution = ' [unresolved]'        else:            if self.max_status < 'valid':                resolution = ' (fails)'            else:                resolution = ' (succeeds)'        return (f"{self.unit.owner.genitive} {self.unit.force} in "                f"{self.unit.location.name} supports "                f"{self.object_order.__str__('support')}{resolution}.")    @property    def province(self):        """ province getter.                """        return self.unit.location.province    def sort_string(self):        """ Returns the string format by which units are sorted.                """        return self.unit.sort_string()    def __supports_move_on__(self, province):        """ Method to test whether self supports a move into a province.        """        if not isinstance(self.object_order, Move):            return False        return self.object_order.target.province is province    def __legalize__(self, orders, game_map, verbose=False):        """ Method to resolve legality of the move.        """        relevant = next((order for order in orders                         if order.unit is self.object_order.unit), None)        reached = [location.province for location in game_map.locations                   if location.id in self.unit.location.connections]        # These two lines should be irrelevant?        if relevant is None:            self.max_status = 'illegal'        elif isinstance(self.object_order, Hold):            if isinstance(relevant, Move):                self.max_status = 'illegal'            elif relevant.province in reached:                self.min_status = 'cut'            else:                self.max_status = 'illegal'        elif isinstance(self.object_order, Move):            if verbose:                print('\tSupporting a move order.')            if not isinstance(relevant, Move):                self.max_status = 'illegal'            elif relevant.target.province in reached:                self.min_status = 'cut'                if verbose:                    print("\tmin_status increased to 'cut'.")            else:                self.max_status = 'illegal'        else:            self.max_status = 'illegal'    def __resolve_attacked__(self, orders, verbose=False):        """ Method to resolve whether the support is cut.        """        targets = [order.target.province for order in orders                   if isinstance(order, Move)                   and order.cutting is True                   and order.unit.owner != self.unit.owner]        if self.province in targets:            self.max_status = 'cut'            if verbose:                print("\tUnit is attacked; max_status is 'cut'.")    def __resolve_left_alone__(self, orders, verbose=False):        """ Method to resolve whether the support is not cut.        """        targets = [order.target.province for order in orders                   if isinstance(order, Move)                   and order.cutting is not False                   and order.unit.owner != self.unit.owner]        if not(self.province in targets):            self.min_status = 'valid'            if verbose:                print("\tUnit is left alone; min_status is 'valid'.")    def resolve(self, variant, orders, verbose=False):        """ Main method to resolve a support.        """        if verbose:            print(f'Resolving support of unit in {self.unit.province}.')        if not self.__resolved__('hold'):            self.__compute_hold_strengths__(orders)        if self.min_status == 'illegal':            self.__legalize__(orders, variant.map, verbose)        if self.min_status > 'illegal':            self.__resolve_attacked__(orders, verbose)            self.__resolve_left_alone__(orders, verbose)    @property    def resolved(self):        """        """        return self.__resolved__('status') and self.__resolved__('hold')