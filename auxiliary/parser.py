#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This module contains the order parser object.

"""

import adjudicator.orders as od
from auxiliary.errors import OrderInputError
from auxiliary.itemlist import ItemList
from auxiliary.lists import translate


class Parser:
    """ An Parser is text order with parsed data.

    """

    def __init__(self, string, game):
        """ Constructor.
 
        """
        self.game = game
        self.map = game.variant.map
        self.string = self.__deabbreviate__(string)

    def __deabbreviate__(self, string):
        """ Takes a string input form a user and adjusts to the format assumed
        by the formatting methods. Also replaces abbreviations with their
        full lenght counterparts.

        """
        words = [word.replace('.', '') for word in string.split(' ')]
        words = translate(words, 
                          self.game.orders_dict, 
                          self.map.prov_dict,
                          self.map.force_dict)        
        # Due to spaces in province names, we need the whole string.
        return ' '.join(words).lower()

    class Decorators():

        @classmethod
        def load_orders(cls, func):
            """ Wrapper function to load named orders.

            """
            def load_orders_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.orders
                except AttributeError:
                    obj.orders = ItemList(obj.string, obj.map.orders)
                return func(*args, **kwargs)
            return load_orders_wrapper

        @classmethod
        def load_provinces(cls, func):
            """ Wrapper function to load named provinces.

            """
            def load_provinces_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.provinces
                except AttributeError:
                    obj.provinces = ItemList(obj.string, obj.map.provinces, first=True)
                return func(*args, **kwargs)
            return load_provinces_wrapper

        @classmethod
        def load_powers(cls, func):
            """ Wrapper function to load named powers.

            """
            def load_powers_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.powers
                except AttributeError:
                    obj.powers = ItemList(obj.string, obj.game.powers)
                return func(*args, **kwargs)
            return load_powers_wrapper

        @classmethod
        def load_numbers(cls, func):
            """ Wrapper function to load named numbers.

            Currently, cannot handle variants with possibly 10 or more builds 
            orders for one power in one year.

            """
            def load_numbers_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.numbers
                except AttributeError:
                    obj.numbers = ItemList(obj.string, range(10))
                return func(*args, **kwargs)
            return load_numbers_wrapper

        @classmethod
        def load_specifiers(cls, func):
            """ Wrapper function to load named numbers.

            """
            def load_specifiers_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.specifiers
                except AttributeError:
                    if obj.game.season.phase == 'Diplomacy':
                        specifiers = obj.unit.specifiers
                    elif obj.game.season.phase == 'Retreats':
                        specifiers = obj.previous.unit.specifiers
                    else:
                        specifiers = obj.forces.loc(0).specifiers
                obj.specifiers = ItemList(obj.string, specifiers)
                return func(*args, **kwargs)
            return load_specifiers_wrapper

        @classmethod
        def load_forces(cls, func):
            """ Wrapper function to load named numbers.

            """
            def load_forces_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.forces
                except AttributeError:
                    obj.forces = ItemList(obj.string, obj.game.forces)
                return func(*args, **kwargs)
            return load_forces_wrapper

        @classmethod
        def identify_unit(cls, func):
            """ Wrapper function to identify the unit the order is given to.

            """
            def identify_unit_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.unit = obj.game.unit_in(obj.provinces.loc(0), require=True)
                except ValueError:
                    raise OrderInputError('Could not identify the unit.')
                return func(*args, **kwargs)
            return identify_unit_wrapper

        @classmethod
        def identify_object(cls, func):
            """ Wrapper function to identify the unit the order is given to.

            """
            def identify_object_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.object
                except AttributeError:
                    try:
                        obj.object = obj.game.unit_in(obj.provinces.loc(1 + obj.reversed), require=True)
                    except AttributeError:
                        obj.object = obj.game.unit_in(obj.provinces.loc(1), require=True)
                    except ValueError:
                        raise OrderInputError('Could not identify the object unit.')
                return func(*args, **kwargs)
            return identify_object_wrapper

        @classmethod
        def identify_order(cls, func):
            """ Wrapper function to identify the unit the order is given to.

            """
            def identify_order_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.previous
                except AttributeError:
                    if obj.game.season.phase != 'Builds':
                        obj.previous = obj.game.order_in(obj.provinces.loc(0), require=True)
                    else:
                        obj.previous = obj.game.adjustment_order(obj.numbers.loc(0), obj.powers.loc(0))
                return func(*args, **kwargs)
            return identify_order_wrapper

        @classmethod
        def is_convoy(cls, func):
            """ Wrapper function to identify the unit the order is given to.

            """
            def is_convoy_wrapper(*args, **kwargs):

                obj = args[0]
                try:
                    obj.convoy
                except AttributeError:
                    obj.convoy = 'convoy' in obj.string
                # Checking whether the unit mey be convoyed.
                # This type or error handling should happend at the resolve stage
                if obj.convoy and 'Convoy' not in obj.unit.force.may_receive:
                    raise OrderInputError(f'Unit may not be convoyed.')
                return func(*args, **kwargs)
            return is_convoy_wrapper

        @classmethod
        def is_reversed(cls, func):
            """ Wrapper function to identify the unit the order is given to.

            """
            def is_reversed_wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    obj.reversed
                except AttributeError:
                    obj.reversed = ' from ' in obj.string
                return func(*args, **kwargs)
            return is_reversed_wrapper


    def new(self):
        """ Returns the parsed order.
        
        """
        return getattr(self, f'parse{self.game.season.phase}')()

    @Decorators.load_orders
    @Decorators.load_provinces
    @Decorators.identify_unit
    def parseDiplomacy(self):
        """ Returns the parsed order during the Diplomacy phase.
        
        """
        return getattr(self, f'parse{self.orders.loc(0)}')()

    def parseHold(self):
        """ Returns a persed move order during the Diplomacy phase.
        
        """
        return od.Hold(self.unit)

    @Decorators.is_convoy
    @Decorators.load_specifiers
    def parseMove(self):
        """ Returns a persed move order during the Diplomacy phase.
        
        """
        specifier = self.specifiers.first(after=self.provinces.pos(1))
        target = self.game.locate(self.unit.force, self.provinces.loc(1),
                                   self.unit.location, specifier, require=True)
        return od.Move(self.unit, self.convoy, target)

    @Decorators.is_reversed
    @Decorators.identify_object
    def parseSupport(self):
        """ Returns a persed support order during the Diplomacy phase.
        
        """
        try:
            return getattr(self, f'parseSupport{self.orders.loc(1)}')()
        except AttributeError:
            raise OrderInputError('Object order may not be support.')

    def parseSupportHold(self):
        """ Returns a parsed support hold order.
        
        """
        return od.Support(self.unit, od.Hold(self.object))    

    @Decorators.load_specifiers
    def parseSupportMove(self):
        """ Returns a parsed support move order.
        
        """
        # Specifier for the target province depends on whether input is
        # in standard or in webDip-reversed format.
        if self.reversed:
            specifier = self.specifiers.first(after=self.provinces.pos(1),
                                              before=self.provinces.pos(2))
        else:
            specifier = self.specifiers.first(after=self.provinces.pos(2))
        target = self.game.locate(self.object.force,
                                  self.provinces.loc(2 - self.reversed),
                                  self.object.location, specifier, 
                                  either=True, require=True)
        return od.Support(self.unit, od.Move(self.object, False, target))

    @Decorators.is_reversed
    @Decorators.identify_object
    def parseConvoy(self):
        """ Returns a persed move order during the Diplomacy phase.
        
        """
        # This kind of error handling should probably happen at the
        # resolve stage.
        if 'Convoy' not in self.unit.location.geography.orders:
            raise OrderInputError(f'Unit may not convoy.')
        if 'Convoy' not in self.object.force.may_receive:
            raise OrderInputError(f'Object unit may not be convoyed.')
        # Possible error if new forces are introduced
        # In the current variants, only Armies may be convoyed,
        target = self.game.locate(self.object.force, 
                                  self.provinces.loc(2 - self.reversed).name,
                                  require=True)
        return od.Convoy(self.unit, od.Move(self.object, True, target))

    @Decorators.load_provinces
    @Decorators.identify_order
    @Decorators.load_specifiers
    def parseRetreats(self):
        """ Adjusts the relevant order during the Retreat phase.
        Gives no output.
        
        """
        if len(self.provinces) == 1:  # interpret as a disband order.
            self.previous.order = od.Disband(self.previous.id, 
                                             self.previous.unit.owner,
                                             self.previous.unit)
        else:  # interpret as a retreat order.
            specifier = self.specifiers.first(after=self.provinces.pos(1))
            target = self.game.locate(self.previous.unit.force, 
                                      self.provinces.loc(1),
                                      self.previous.unit.location,
                                      specifier, require=True)
            self.previous.order = od.Move(self.previous.unit, False, target)

    @Decorators.load_numbers
    @Decorators.load_powers
    @Decorators.identify_order
    def parseBuilds(self):
        """ Adjusts the relevant order during the Build phase.
        Gives no output.
        
        """
        if isinstance(self.previous, od.Disband):
            self.parseBuildsDisband()
        elif isinstance(self.previous, od.Build):
            self.parseBuildsBuild()

    @Decorators.load_provinces
    @Decorators.load_forces
    @Decorators.load_specifiers
    def parseBuildsBuild(self):
        """ Adjusts the relevant build order during the Build phase.
        Gives no output.
        
        """
        if 'postpone' in self.string or 'do not use' in self.string:
            self.previous.postpone()
        else:
            target = self.game.locate(self.forces.loc(0), 
                                      self.provinces.loc(0),
                                      specifier=self.specifiers.loc(0, require=False),
                                      require=True)
            self.previous.set_force(self.forces.loc(0))
            self.previous.set_location(target)

    @Decorators.load_provinces
    def parseBuildsDisband(self):
        """ Adjusts the relevant disband order during the Build phase.
        Gives no output.
        
        """
        self.previous.set_unit(self.game.unit_in(self.provinces.loc(0), True))

    @Decorators.load_provinces
    @Decorators.identify_unit
    @Decorators.identify_order
    def old(self):
        """ Returns the order which is to be replaced.
        Should only be called during the Diplomacy phase.
        
        """
        assert self.game.season.phase == 'Diplomacy'
        return self.previous
        