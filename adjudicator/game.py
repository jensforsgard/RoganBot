#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This mode contains the Game class. An instance of this class is a game
of Diplomacy.

The game class is currently a 'monster class', which contains most methods
to parse input and resolve orders.

Attributes:
----------
    Game

"""


import geopandas as geo
from fiona.errors import DriverError

import adjudicator.orders as od
import adjudicator.variant as vr
import adjudicator.board as bd
import graphics.graphics as graphics

from auxiliary.lists import (first, translate)
from auxiliary.errors import (OrderInputError, GameError, AdjudicationError)
from auxiliary.itemlist import ItemList
from auxiliary.classes import dict_string




class Game:
    """ A game of Diplomacy.

    This monster class holds all information of a game, including the graphical
    elements to draw a map. In addition, it holds all methods which govern
    adjudicating the game.

    Attributes:
        page: string or None
            Name of host of the game.
        identifier: string or None
            Unique identifier of the game.
        variant: Variant
        season: Season
        powers: list of Powers
            The powers playing in the game.
        forces: list of Forces
            The forces included in the game.
        units: list of Units
            The current units in the game.
        provinces: list of Provinces
            The provinces of the map.
        home_centers: dictionary
            Dictionary encoding the home centers of each power.
        supply_centers: dictionary
            Dictionary encoding the currently owned centers of each power.
        orders: list of orders
            List of orders for the units in the game in the current phase.
        winner: Power or None
            The winner of the game, or None if no winner has been determined.
        position_archive: list
            List of all previous positions that occured in the game.
        order_archive: list
            List of all order sets submitted each phase.
        graphics: geopandas GeoDataFrame
            graphical information to plot the game
        shift: float
            The shift in position applied in various plotting features. Depends
            on the projection of the map.

    """

    # Custom short forms, which are map and variant independent.
    orders_dict = {'-': 'move', 'S': 'support', 'C': 'convoy', 'H': 'hold',
                   'B': 'build', 'D': 'disband', 'R': 'retreat',
                   'A': 'army', 'F': 'fleet', 'St': 'Saint', 
                   'destroy': 'disband'}

    def __init__(self, variant_name, page=None, identifier=None):
        """ Constructor.

        Parameters
        ----------
        variant_name: string
        page: string, optional
            The name of host of the game.
        identifier: string, optional
            The unique identifier of the game.

        """
        self.page = page
        self.identifier = identifier
        self.variant = vr.Variant(variant_name)
        self.variant.load()
        self.season = bd.Season('Spring', 'Pregame',
                                self.variant.starting_year)
        # Immutables
        self.powers = self.variant.powers
        self.forces = self.variant.map.forces
        self.provinces = self.variant.map.provinces
        # Mutables; will be loaded once the game begins
        self.units = []
        self.home_centers = {}
        self.supply_centers = {}
        self.orders = []
        self.winner = None
        self.position_archive = []
        self.order_archive = []
        # Graphic objects; will be loaded if needed
        self.graphics = None
        self.shift = None


    def __str__(self):
        """ Print method.

        """
        return (f'Game variant: {self.variant.name}.\n'
                f'Game map: {self.variant.map.name}.\n'
                f'Season: {self.season.__str__()}')


    def info(self, string='units', pos=-1):
        """ Retrieves informatino as a string.

        """
        options = {'abbreviations', 'archive', 'center counts', 'centers', 
                   'map', 'units', 'variant', 'orders', 'options',
                   'provinces', 'season', 'supply centers'}
        if string not in options:
            raise ValueError(f'Option "{string}" not recognized.')
        elif string == 'options':
            return str(options)
        elif string == 'variant':
            return str(self.variant)
        elif string == 'map':
            return str(self.variant.map)
        elif string == 'season':
            return str(self.season)
        elif string == 'abbreviations':
            return f'{dict_string(self.orders_dict)}\n{self.variant.map.info(string)}'
        elif string == 'provinces':
            return self.variant.map.info(string)
        elif string == 'supply centers':
            return self.variant.map.info(string)
        elif self.season.phase == 'Pregame':
            raise GameError('Option "{string}" not available in Pregame phase.')
        elif string == 'centers':
            return dict_string(self.supply_centers, deliminator=':')
        elif string == 'center counts':
            return dict_string(self.supply_centers, func=len, deliminator=':')
        elif string == 'units':
            self.__sort_units__()
            return '\n'.join([f'{unit}' for unit in self.units])
        elif string == 'orders':
            self.__sort_orders__()
            return '\n'.join([f'{order}' for order in self.orders])
        elif string == 'archive':
            return '\n'.join([f'{entry}' for entry in self.order_archive[pos]])


    def display(self, string, pos=-1):
        """ Prints information.
        
        """
        if string == 'position':
            self.show()
        else:
            print(self.info(string, pos))
        

    def current_position(self):
        """ Returns a dictionary with a copy of the game's current position.

        """
        return {'season': self.season.name,
                'phase': self.season.phase,
                'year': self.season.year,
                'units': [{'force': unit.force.name,
                           'owner': unit.owner.name,
                           'location': unit.location.id}
                          for unit in self.units],
                'centers': {power.name: [province.name for province in
                                         self.supply_centers[power]]
                            for power in self.powers}}


    def __archive_position__(self):
        """ Archives the current position.

        """
        self.position_archive.append(self.current_position())


    def __archive_orders__(self):
        """ Archives the current set of orders.

        """
        self.__sort_orders__()
        self.order_archive.append([str(order) for order in self.orders])


    def __unit_color__(self, power):
        """ Returns the color the unit should be given when plotted.

        """
        return self.variant.unit_colors[power.name]


    def show(self):
        """ Plots the current position. 

        """
        graphics.show(self)


    def start(self):
        """ Starts the game. That is, moves phase Pregame to Spring at starting
        year; sets up home centers and units in starting positions.

        """
        assert self.season.phase == 'Pregame', ('The Game is already started.')
        self.season.progress()

        for entry in self.variant.starting_positions:
            self.add_unit(entry['force'], entry['power'], entry['location'])
            # The add_unit method also adds a standard hold order.

        for power in self.powers:
            # Home centers are starting positions
            self.supply_centers[power] = set(self.occupied_provinces(power))
            self.home_centers[power] = self.supply_centers[power].copy()

        self.__archive_position__()


    def reset(self):
        """ Resets the game to Pregame settings.

        """
        self.season = bd.Season('Spring', 'Pregame', self.variant.starting_year)
        self.units = []
        self.orders = []
        self.position_archive = []
        self.order_archive = []
        self.supply_centers = {}
        self.home_centers = {}
        self.winner = None


    def rollback(self):
        """ Rolls back the game one turn. 
        
        """
        self.season.relapse()  # Includes consistency check
        orders = self.order_archive[-1]  # Remeber last phase's orders
        del self.order_archive[-1]
        del self.position_archive[-1]
        self.winner = None
        position = self.position_archive[-1]
        for power in self.powers:
            # Reset supply ceter ownership
            self.supply_centers[power] = set(self.variant.map.instances(
                position['centers'][power.name], bd.Province))
            # Check if there was already a winner
            if len(self.supply_centers[power]) >= self.variant.win_condition:
                self.winner = power
        # Reset the lists of units and orders
        self.units = []
        self.orders = []
        for entry in position['units']:
            self.add_unit(**entry, overrule=True)
        # Add the unresolved orders for the last phase
        self.order(orders)


    def __compute_shift__(self):
        """ Computes the shift for the plotting retreating units.
        
        """
        ycoords = [point.y for point in 
                   self.graphics[self.graphics.point == True].geometry]
        self.shift = (max(ycoords) - min(ycoords))*.01        


    def __load_graphics__(self):
        """ Loads the GeoDataFrame from the graphics folder.

        """
        path = f'graphics/{self.variant.map.name}.geojson'
        try:
            self.graphics = geo.read_file(path)
            self.graphics.to_crs('ESRI:54027', inplace=True)
        except DriverError:
            raise GameError('No graphics file found.')
        self.__compute_shift__()


    def __sort_units__(self):
        """ Sorts the list of units according to owner and unit id.

        """
        self.units.sort(key=lambda unit: f'{unit.owner.name}{unit.id}')


    def __sort_orders__(self):
        """ Sorts the list of orders.

        """
        def rank_string(order):
            if self.season.phase == 'Builds':
                owner = order.owner.name
                idn = order.id
            else:
                owner = order.unit.owner.name  
                idn = order.unit.id
            return f'{owner}{idn}'        
        self.orders.sort(key=rank_string)


    def __sort_by_relevance__(self):
        """ Sorts the list of orders by order type; for a faster adjudication
        procedure.

        """
        self.orders.sort(key=lambda order: order.relevance)


    def unit_in(self, province, require=False, any_=False):
        """ Retrieves the unit in a province. Throws and error if an output is
        required but no unit can be identified. 

        Parameters:
        -----------
        province: Province
        require: boolean, optional
            Encodes whether an output is required. Default is False.
        any_: boolean, optional
            Whether to check for _the_ unit or _any_ unit. Relevant only in
            retreat phases.
        """
        assert any_ or self.season.phase != 'Retreats'
        if type(province) is str:
            province = self.instance(province, bd.Province)
        generator = (unit for unit in self.units if unit.province is province)
        answer = next(generator, None)
        if require and (answer is None):
            raise OrderInputError(f'There is no unit in {province.name}.')
        return answer


    def order_of(self, unit):
        """ Retrieves the order of a unit.

        """
        generator = (order for order in self.orders if order.unit is unit)
        return next(generator, None)


    def order_in(self, province, require=False, orders=None):
        """ Retrieves the order of a unit in a province. Throws an error if
        an order is required but not available. You may restrict the search
        to a specific set of orders.

        """
        if orders is None:
            orders = self.orders
        generator = (order for order in orders if order.province is province)
        answer = next(generator, None)
        if require and answer is None:
            raise OrderInputError(f'No unit in {province.name}.')
        return answer


    def adjustment_order(self, number, power, require=False):
        """ Retrieves the adjustement order with a given id for a given power.
        Throws an error if an order is required but not available.

        """
        assert self.season.phase == 'Builds'
        generator = (order for order in self.orders
                     if order.id == number and order.owner.name == str(power))
        order = next(generator, None)
        if require and order is None:
            raise OrderInputError(f'Could not identify the adjustment order.')
        return order


    def units_of(self, power):
        """ Returns a list of the units belonging to a power.

        """
        return [unit for unit in self.units if unit.owner is power]


    def occupied_provinces(self, power):
        """ Returns a list of the provinces occupied by the units of a power.

        """
        return [unit.province for unit in self.units_of(power)]


    def build_orders_of(self, power):
        """ Returns a list of the adjustment orders given to the units of a
        power.

        """
        assert self.season.phase == 'Builds'
        return [order for order in self.orders if order.owner is power]


    def open_home_centers(self, power):
        """ Returns a lists the available home centers belonging to a power.

        """
        home = self.home_centers[power]
        owned = home.intersection(self.supply_centers[power])
        return owned.difference(self.occupied_provinces(power))


    def instance(self, name, class_or_class_name, require=False):
        """ Returns an instance of a class identified by its name.

        """
        classes = {'power': vr.Power,
                   'force': bd.Force,
                   'province': bd.Province,
                   'geography': bd.Geography}
        if isinstance(class_or_class_name, str):
            class_type = classes[class_or_class_name.lower()]
        else:
            class_type = class_or_class_name
        if getattr(class_type, '__module__', None) == bd.__name__:
            answer = self.variant.map.instance(name, class_type)
        elif getattr(class_type, '__module__', None) == vr.__name__:
            answer = self.variant.instance(name, class_type)
        else:
            raise GameError('Could not identify the class.')
        if require and answer is None:
            raise GameError('Could not identify the instance.')
        return answer


    def locate(self, force, name, origin=None, specifier=None, require=False,
               either=False):
        """ Returns the location of a unit in a given province, if uniquely
        determined by the parameters. Throws an error is an output is erquired
        but could not be determined.

        """
        location = self.variant.map.locate(force, name, origin, specifier,
                                           either)
        if require and location is None:
            raise GameError(f'Could not locate {force.name} in {name}.')
        return location


    def __unresolved_count__(self):
        """ Counts the number of unresolved orders.

        """
        return len([order for order in self.orders if not order.resolved])


    def __next_unit_id__(self):
        """ Retrieves the successor of the largest unit id.

        """
        if len(self.units) == 0:
            return 1
        else:
            return max([unit.id for unit in self.units]) + 1


    def add_unit(self, force, owner, location, overrule=False):
        """ Adds a unit to the game in a given location. If we are in the
        Diplomacy phase, a standard order is also added.

        """
        message = 'You cannot manually add unit during the retreat phase.'
        assert overrule or self.season.phase != 'Retreats', message
        # Retrieve classes if input was strings.
        if not isinstance(force, bd.Force):
            force = self.instance(force, bd.Force, require=True)
        if not isinstance(owner, vr.Power):
            owner = self.instance(owner, vr.Power, require=True)
        if not isinstance(location, bd.Location):
            location = self.locate(force, location, require=True)
        # Check that the given location is available.
        if not self.unit_in(location.province, any_=True) is None:
            raise GameError('Named province already contains a unit.')
        unit = vr.Unit(self.__next_unit_id__(), owner, force, location)
        self.units.append(unit)
        if self.season.phase == 'Diplomacy':
            self.orders.append(od.Hold(unit))


    def delete_unit(self, province_or_unit):
        """ Deletes a unit from the game.

        """
        assert self.season.phase != 'Builds'
        # Adjust for input format.
        if isinstance(province_or_unit, vr.Unit):
            unit = province_or_unit
        elif isinstance(province_or_unit, str):
            unit = self.unit_in(self.instance(province_or_unit, 'province'))
        elif isinstance(province_or_unit, bd.Province):
            unit = self.unit_in(province_or_unit)
        # Delete the unit and its order.
        if not isinstance(unit, vr.Unit):
            raise ValueError('Could not identify the unit to be removed.')
        self.orders = [ordr for ordr in self.orders if ordr.unit is not unit]
        self.units.remove(unit)


    def __update_order__(self, order, old=None):
        """ Replaces an old order with a new order. If the order is given
        during the Diplomacy phase, the the old order is identified by the
        unit. During other phases, you may specify the order to be replaced.

        """
        if self.season.phase == 'Diplomacy':
            if order.unit not in self.units:
                raise ValueError('Order is for a unit which is not in game.')
            old = self.order_of(order.unit)
        if old not in self.orders:
            raise GameError('The order to be replaced is not in the game.')
        self.orders = [entry for entry in self.orders if entry is not old]
        self.orders.append(order)


    def __adjust_supply_centers__(self):
        """ Adjusts the supply center count.

        """
        supply_centers = set(self.variant.map.supply_centers)
        for power in self.powers:
            unit_locations = set(self.occupied_provinces(power))
            occupied = unit_locations.intersection(supply_centers)
            # It is important that the order is: first remove, then add.
            for second_power in self.powers:
                self.supply_centers[second_power].difference_update(occupied)
            self.supply_centers[power].update(occupied)


    def __format__(self, string):
        """ Takes a string input form a user and adjusts to the format assumed
        by the formatting methods. Also replaces abbreviations with their
        full lenght counterparts.

        """
        words = [word.replace('.', '') for word in string.split(' ')]
        words = translate(words, 
                          self.orders_dict, 
                          self.variant.map.prov_dict,
                          self.variant.map.force_dict)        
        # Due to spaces in province names, we need the whole string.
        return ' '.join(words).lower()


    def order(self, string_or_list):
        """  Accepts a string or a list of strings as input. Passes on the 
        adjusted lists of words to the phase specific input methods.

        """
        if self.season.phase not in ['Diplomacy', 'Retreats', 'Builds']:
            raise OrderInputError('No orders expected for the current phase.')
        if isinstance(string_or_list, list):
            for string in string_or_list:
                self.order(string)
        else:
            string = self.__format__(string_or_list)
            getattr(self, f'__input_{self.season.phase.lower()}__')(string)


    def __format_move__(self, text, named_orders):
        """ Formats a move order from a string.

        """
        provinces = ItemList(text, self.provinces, first=True)
        # Retrieve source province and unit
        source = provinces.loc(0)
        unit = self.unit_in(source, require=True)
        # Determine target location.
        province = provinces.loc(1)
        text = text[provinces.pos(0):]
        specifier = ItemList(text, unit.specifiers).loc(0, require=False)
        target = self.locate(unit.force, province.name,
                             unit.location, specifier, True)
        convoy = 'Convoy' in named_orders
        if convoy and 'Convoy' not in unit.force.may_receive:
            raise OrderInputError(f'{text}: Unit may not be convoyed.')
        return od.Move(unit, convoy, target)


    def __format_hold__(self, text, named_orders):
        """ Formats a hold order from a string.

        """
        province = ItemList(text, self.provinces, first=True).loc(0)
        unit = self.unit_in(province, True)
        return od.Hold(unit)


    def __format_support__(self, text, orders):
        """ Formats a support order from a string.

        """
        provinces = ItemList(text, self.provinces, first=True)
        unit = self.unit_in(provinces.loc(0), True)
        # N.B. referring to the __format_hold__ method would be slower.
        if orders.loc(1) == 'Hold':
            ob_unit = self.unit_in(provinces.loc(1), True)
            return od.Support(unit, od.Hold(ob_unit))
        # Due to the webDiplomacy reverse input format, referring to the
        # __format_move__ method is not possible.
        elif orders.loc(1) == 'Move':
            flipped = (' from ' in text)
            obj_unit = self.unit_in(provinces.loc(1 + flipped), True)    
            province = provinces.loc(2 - flipped)
            pos = provinces.pos(2 - flipped)
            spec = ItemList(text, unit.specifiers).first_after(pos)
            target = self.locate(obj_unit.force, province,
                                 obj_unit.location, spec, True, True)
            return od.Support(unit, od.Move(obj_unit, False, target))
        else:
            raise OrderInputError('Object may not receive support.')



    def __format_convoy__(self, text, named_orders):
        """ Formats a convoy order from a string.

        """
        provinces = ItemList(text, self.provinces, first=True)
        unit = self.unit_in(provinces.loc(0), True)
        flipped = (' from ' in text)
        object_unit = self.unit_in(provinces.loc(1 + flipped), True)
        target = provinces.loc(2 - flipped)
        if 'Convoy' not in unit.location.geography.orders:
            raise OrderInputError(f'Unit may not convoy.')
        if 'Convoy' not in object_unit.force.may_receive:
            raise OrderInputError(f'Object unit may not be convoyed.')
        # Possible error if new forces are introduced: In the current variants,
        # only Armies may be convoyed,
        target = self.locate(object_unit.force, target.name, require=True)
        return od.Convoy(unit, od.Move(object_unit, True, target))


    def __input_diplomacy__(self, string):
        """ Method to input orders during the Diplomacy phase. Identifies the
        class of the order and calls the corresponding class specific
        formatting method.

        """
        orders = ItemList(string, self.variant.map.orders)
        attr = f'__format_{orders.loc(0).lower()}__'
        order = getattr(self, attr)(string, orders)
        self.__update_order__(order)



    def __input_retreats__(self, text):
        """ Method to input orders during the Retreat phase.

        """
        provinces = ItemList(text, self.provinces, first=True)
        old = self.order_in(provinces.loc(0), True)
        unit = old.unit
        if len(provinces) == 1:  # interpret as a disband order.
            new = od.Disband(old.id, unit.owner, unit)
        else:  # interpret as a retreat order.
            target_prov = provinces.loc(1)
            subtext = text[provinces.pos(1):]
            spec = ItemList(subtext, unit.specifiers).loc(0, require=False)
            target = self.locate(unit.force, target_prov.name, unit.location,
                                 spec, True)
            new = od.Move(unit, False, target)
        retreat = od.Retreat(old.id, unit, new, old.forbidden)
        self.__update_order__(retreat, old)


    def __input_builds__(self, text):
        """ Method to input orders during the Build phase.

        """
        # Cannot handle variants with possible 10 or mroe builds in one year.
        number = next((int(x) for x in text if x.isnumeric()), None)
        power = ItemList(text, self.powers).loc(0)
        order = self.adjustment_order(number, power, True)
        if 'postpone' in text or 'default' in text or 'do not use' in text:
            order.postpone()
        else:
            province = ItemList(text, self.provinces, first=True).loc(0)
            if isinstance(order, od.Disband):
                unit = self.unit_in(province, True)
                order.set_unit(unit)
            elif isinstance(order, od.Build):
                force = ItemList(text, self.forces).loc(0)
                spec = ItemList(text, force.specifiers).loc(0, require=False)
                location = self.locate(force, province, require=True,
                                       specifier=spec)
                order.set_force(force)
                order.set_location(location)


    def __resolve_orders__(self, verbose=False):
        """ Method to resolve orders.

        """
        for order in self.orders:
            if not(order.resolved):
                order.resolve(self.variant, self.orders, verbose)


    def __resolve_diplomacy__(self, verbose=False):
        """ Method to resolve orders during the diplomacy phase.

        """
        self.__sort_by_relevance__()
        counter = 1
        while counter < 3:
            unresolved = self.__unresolved_count__()
            # Set larger initial value  to start the second loop
            previous = unresolved + 1
            while previous > unresolved:
                self.__resolve_orders__(verbose)
                previous = unresolved
                unresolved = self.__unresolved_count__()
                if unresolved == 0:
                    break
            if unresolved == 0:
                break
            if counter == 1:
                self.__resolve_paradoxes__()
            if counter == 2:
                self.__resolve_circular_movement__()
            counter += 1


    def __resolve_paradoxes__(self, verbose=False):
        """ Method to resolve paradoxes.

        """
        assert self.season.phase == 'Diplomacy'
        for order in self.orders:
            if (isinstance(order, od.Move) and order.convoy
                and not order.resolved):
                order.set_('cutting', False)
                order.set_('dislodging', False)


    def __resolve_circular_movement__(self, varbose=False):
        """ Method to resolve circular movement.

        """
        assert self.season.phase == 'Diplomacy'
        for order in self.orders:
            if isinstance(order, od.Move) and not order.resolved:
                order.set_('cutting', False)
                order.set_('dislodging', False)
                order.set_('failed', False)
                order.set_resolved()


    def __resolve_retreats__(self, verbose=False):
        """ Method to resolve retreats.

        """
        counter = 1  # Might need two for loops.
        while counter < len(self.orders) + 1:
            self.__resolve_orders__(verbose)
            if self.__unresolved_count__() == 0:
                break
            counter += 1


    def __resolve_builds__(self, verbose=False):
        """ Method to resolve builds.

        """
        # It is faster to resolve adjustment 'globally' intsead of calling
        # resolve methods for each separate adjustment order.
        province_methods = {od.Build: self.open_home_centers,
                            od.Disband: self.occupied_provinces}
        for power in self.powers:
            orders = self.build_orders_of(power)
            if len(orders) == 0:
                continue
            adjustment = type(first(orders))
            provinces = province_methods[adjustment](power)
            # Pick the first valid order for each province.
            valid = []
            for province in provinces:
                valid.append(self.order_in(province, orders=orders))
            for order in orders:
                if order not in valid:
                    order.invalid_action(self.units, self.orders)
                order.resolved = True


    def __execute_diplomacy__(self):
        """ Method to execute successful moves for adjudication of Diplomacy
        phase.

        """
        moves = [order for order in self.orders if isinstance(order, od.Move)]
        valid = [order for order in moves if order.moves()]
        for order in valid:
            order.unit.move_to(order.target)


    def __execute_retreats__(self):
        """ Method to execute retreats.

        """
        for retreat in self.orders:
            if isinstance(retreat.order, od.Disband) or retreat.disbands:
                self.delete_unit(retreat.order.unit)
            elif isinstance(retreat.order, od.Move):
                retreat.unit.move_to(retreat.order.target)


    def __execute_builds__(self):
        """ Method to execute builds.

        """
        for order in self.orders:
            if isinstance(order, od.Disband):
                self.units = [entry for entry in self.units 
                              if entry is not order.unit]
            if isinstance(order, od.Build) and not order.failed:
                self.add_unit(order.force, order.owner, order.location)


    def __setup_diplomacy__(self):
        """ Method to setup the Diplomacy phase.

        """
        self.orders = [od.Hold(unit) for unit in self.units]


    def __setup_retreats__(self):
        """ Method to setup the Retreat phase.

        """
        blocked = od.flatten([order.blocks() for order in self.orders])
        blocked = list(set(blocked))
        retreats = []
        for order in self.orders:
            if not order.moves():
                continue
            # Warning: Diplomacy phase has been executed, meaning that in case
            # of retreats there is more than one unit in a province.
            object_order = self.order_in(order.target.province)
            if object_order is None or object_order.moves():
                continue
            unit = object_order.unit
            if order.convoy:
                units_blocked = blocked
            else:
                units_blocked = blocked + [order.province]
            disband = od.Disband(0, unit.owner, unit)
            retreats.append(od.Retreat(0, unit, disband, units_blocked))
        self.orders = retreats


    def __setup_builds__(self):
        """ Method to setup the Build phase.

        """
        self.orders = []
        self.__adjust_supply_centers__()
        for power in self.powers:
            count = len(self.supply_centers[power])-len(self.units_of(power))
            if count > 0:
                count = min(count, len(self.open_home_centers(power)))
                builds = [od.Build(j+1, power) for j in range(count)]
                self.orders = self.orders + builds
            elif count < 0:
                disbands = [od.Disband(j+1, power) for j in range(-count)]
                self.orders = self.orders + disbands


    def conclude(self, mute):
        """ Method to conclude the game if there is a winner.

        """
        assert self.winner is None, 'Game has already concluded.'
        for power in self.powers:
            if len(self.supply_centers[power]) >= self.variant.win_condition:
                self.winner = power
                if not mute:
                    print(f'Game won by {power.name}.')


    def adjudicate(self, conclude=True, mute=False, verbose=False):
        """ Main method to adjudicat the game.

        """
        if self.winner is not None:
            print('Winner determined.')
        assert self.season.phase in ['Diplomacy', 'Retreats', 'Builds']
        getattr(self, f'__resolve_{self.season.phase.lower()}__')(verbose)
        self.__archive_orders__()
        if self.__unresolved_count__() != 0:
            raise AdjudicationError('Resolution ended with unresolved orders.')
        getattr(self, f'__execute_{self.season.phase.lower()}__')()
        self.season.progress()  # N.B. this will change the season.phase
        getattr(self, f'__setup_{self.season.phase.lower()}__')()
        if conclude:
            self.conclude(mute)
        self.__archive_position__()
        # If following phase requires no orders, then move on automatically
        if len(self.orders) == 0 and self.winner is None:
            self.adjudicate(conclude=conclude, mute=mute, verbose=verbose)