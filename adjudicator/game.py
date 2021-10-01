""" The Game class

"""

import geopandas as geo
from fiona.errors import DriverError

import graphics.graphics as graphics

from adjudicator import (
    Force, Geography, Location, Power, Province, Season, Unit, Variant
)
from adjudicator.orders import (
    Build, Disband, Hold, Move, Retreat, Support
)
from adjudicator.orders.lib import (
    BuildOrders, DiplomacyOrders, RetreatOrders
)
from adjudicator.wrappers import require

from lib.lists import (first, flatten)
from lib.errors import (OrderInputError, GameError, AdjudicationError)
from lib.classes import dict_string
from lib.archive import (OrderArchive, PositionArchive)
from lib.wrappers import (builds, pregame, province_or_unit)
from lib.parser import Parser


class Game:
    """ A game of Diplomacy.
    How it works: The class holds all information regarding a game of
    Diplomacy, including the current state of the game. It also holds
    master methods to adjudicate the game.

    Initiate an instance by providing the name, as a string, of the
    variant of the game.

    """

    # Custom abbreviations, which are map and variant independent.
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
        self.variant = Variant(variant_name)
        self.variant.load()
        self.season = Season(self.variant.starting_year)
        # Immutables
        self.powers = self.variant.powers
        self.forces = self.variant.map.forces
        self.provinces = self.variant.map.provinces
        # Mutables; will be loaded once the game begins
        self.units = []
        self.home_centers = {}
        self.supply_centers = {}
        self.orders = DiplomacyOrders(Hold)
        self.winner = None
        self.position_archive = PositionArchive()
        self.order_archive = OrderArchive()
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
        """ Retrieves information in a string format.

        """
        # Options with print values should be stored in a dictionary.
        options = {'abbreviations', 'center counts', 'centers', 'map', 'units',
                   'variant', 'order archive', 'orders', 'options',
                   'position archive', 'provinces', 'season', 'supply centers'}
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
            return self.variant.map.info('supply_centers')
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
            self.orders.sort()
            return '\n'.join([f'{order}' for order in self.orders])
        elif string == 'order archive':
            return self.order_archive.__str__(pos)
        elif string == 'position archive':
            return self.position_archive.__str__(pos)

    def display(self, string, pos=-1):
        """ Prints information.
        
        """
        if string == 'position':
            self.show()
        else:
            print(self.info(string, pos=pos))
        
    def current_position(self):
        """ Returns a dictionary with a copy of the game's current position.

        """
        return self.position_archive.last()

    def __archive_position__(self):
        """ Archives the current position.

        """
        self.position_archive.enter(self)

    def __archive_orders__(self):
        """ Archives the current set of orders.

        """
        self.order_archive.enter(self)

    def __unit_color__(cls, power):
        """ Returns the color the unit should be given when plotted.

        """
        return cls.variant.unit_colors[power.name]

    def show(self):
        """ Plots the current position. 

        """
        graphics.show(self)

    @pregame
    def start(self):
        """ Starts the game. That is, moves phase Pregame to Spring at starting
        year; sets up home centers and units in starting positions.

        """
        self.season.progress()
        for entry in self.variant.starting_positions:
            self.add_unit(**entry)  # Also adds default Hold order.
        for power in self.powers:
            self.supply_centers[power] = set(self.occupied_provinces(power))
            self.home_centers[power] = self.supply_centers[power].copy()
        self.__archive_position__()

    def reset(self):
        """ Resets the game to Pregame settings.

        """
        self.season.reset(self.variant)
        self.units = []
        self.orders = DiplomacyOrders(Hold)
        self.position_archive.reset()
        self.order_archive.reset()
        self.supply_centers = {}
        self.home_centers = {}
        self.winner = None

    def rollback(self):
        """ Rolls back the game one turn. 
        
        """
        self.season.rollback()  # Includes consistency check
        orders = self.order_archive.last()  # Remember the last phase's orders
        self.order_archive.rollback()
        self.position_archive.rollback()
        self.position_archive.setup(self)  # Setup according to last archive
        self.conclude(mute=True, assume=False)  # Check for a winner
        self.order(orders)  # Enter the last phase's orders

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

    def __compute_shift__(self):
        """ Computes the shift for the plotting retreating units.
        
        """
        assert self.graphics is not None
        ycoords = [pt.y for pt in self.graphics[self.graphics.point==True].geometry]
        self.shift = (max(ycoords) - min(ycoords))*.01   

    def __sort_units__(self):
        """ Sorts the list of units according to owner and unit id.

        """
        self.units.sort(key=lambda unit: unit.sort_string())

    def __province__(self, province):
        """ Tries to identify a province if input is a string.
        
        """
        if type(province) is str:
            return self.instance(province, Province, require=True)
        else:
            return province

    @require
    def unit_in(self, province, any_=False):
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
        province = self.__province__(province)
        generator = (unit for unit in self.units if unit.province is province)
        return next(generator, None)

    @builds
    @require
    def adjustment_order(self, number, power):
        """ Retrieves the adjustement order with a given id for a given power.
        Throws an error if an order is required but not available.

        """
        generator = (order for order in self.orders
                     if order.id == number and order.owner.name == str(power))
        return next(generator, None)

    def units_of(self, power):
        """ Returns a list of the units belonging to a power.

        """
        return [unit for unit in self.units if unit.owner is power]

    def occupied_provinces(self, power):
        """ Returns a list of the provinces occupied by the units of a power.

        """
        return [unit.province for unit in self.units_of(power)]

    @builds
    def build_orders_of(self, power):
        """ Returns a list of the adjustment orders given to the units of a
        power.

        """
        return [order for order in self.orders if order.owner is power]

    def open_home_centers(self, power):
        """ Returns a lists the available home centers belonging to a power.

        """
        home = self.home_centers[power]
        owned = home.intersection(self.supply_centers[power])
        return owned.difference(self.occupied_provinces(power))

    @require
    def instance(self, name, class_or_class_name):
        """ Returns an instance of a class identified by its name.

        """
        classes = {'power': Power,
                   'force': Force,
                   'province': Province,
                   'geography': Geography}
        if isinstance(class_or_class_name, str):
            class_type = classes[class_or_class_name.lower()]
        else:
            class_type = class_or_class_name
        if class_type in (Force, Geography, Province):
            return self.variant.map.instance(name, class_type)
        if class_type == Power:
            return self.variant.instance(name, class_type)
        elif getattr(class_type, '__module__', None) == vr.__name__:
            return self.variant.instance(name, class_type)
        else:
            raise GameError('Class not within range of the instance method.')

    @require
    def locate(self, force, name, origin=None, specifier=None, either=False):
        """ Returns the location of a unit in a given province, if uniquely
        determined by the parameters. Throws an error is an output is erquired
        but could not be determined.

        """
        return self.variant.map.locate(force, name, origin, specifier, either)


    def __unresolved_count__(self):
        """ Counts the number of unresolved orders.

        """
        return len([order for order in self.orders if not order.resolved])

    def __next_unit_id__(self):
        """ Retrieves the successor of the largest unit id.

        """
        try:
            return max([unit.id for unit in self.units]) + 1
        except ValueError:
            return 1

    def add_unit(self, force, power, location, overrule=False):
        """ Adds a unit to the game in a given location. If we are in the
        Diplomacy phase, a standard order is also added.

        """
        message = 'You cannot manually add unit during the retreat phase.'
        assert overrule or self.season.phase != 'Retreats', message
        # Retrieve classes if input was strings.
        if not isinstance(force, Force):
            force = self.instance(force, Force, require=True)
        if not isinstance(power, Power):
            power = self.instance(power, Power, require=True)
        if not isinstance(location, Location):
            location = self.locate(force, location, require=True)
        # Check that the given location is available.
        if not self.unit_in(location.province, any_=True) is None:
            raise GameError('Named province already contains a unit.')
        unit = Unit(self.__next_unit_id__(), power, force, location)
        self.units.append(unit)
        if self.season.phase == 'Diplomacy':
            self.orders.insert(Hold(unit))

    def add_units(self, list_of_units):
        """ Adds several units to the game.
        
        """
        for unit in list_of_units:
            self.add_unit(*unit)

    @province_or_unit
    def delete_unit(self, unit):
        """ Deletes a unit from the game.

        """
        if self.season.phase != 'Builds':
            self.orders.remove_unit(unit)

        self.units.remove(unit)

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

    def clear(self):
        """ Method to clear the board from all units.
        
        """
        while len(self.units) > 0:
            self.delete_unit(self.units[0])

    # Should be wrapped in a list_input wrapper
    def order(self, string_or_list):
        """  Main method to input orders. Accepts a string or a list of strings
        as input. Parses the input and replaces (Diplomacy phase) or updates
        (Retreat and Build phases) the relevant orders. 

        """
        if isinstance(string_or_list, list):
            for string in string_or_list:
                self.order(string)
        else:
            parser = Parser(string_or_list, self)
            if self.season.phase == 'Diplomacy':
                self.orders.remove(parser.old())
                self.orders.insert(parser.new())
            elif self.season.phase in ['Retreats', 'Builds']:
                # In Retreat and Build phases, the orders are updated
                # and not replaced.
                parser.new()
            else:
                raise OrderInputError('No orders expected for the current phase.')

    def __resolve_orders__(self, verbose=False):
        """ Method to resolve orders.

        """
        for order in self.orders:
            if not(order.resolved):
                order.resolve(self.variant, self.orders, verbose)

    def __resolve_diplomacy__(self, verbose=False):
        """ Method to resolve orders during the diplomacy phase.

        """
        self.orders.sort(by='relevance')
        for order in self.orders:
            if isinstance(order, Move):
                order.__adjacent_convoy__(self.orders)

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
            if isinstance(order, Move) and order.convoy and not order.resolved:
                order.set_('cutting', False)
                order.set_('dislodging', False)

    def __resolve_circular_movement__(self, varbose=False):
        """ Method to resolve circular movement.

        """
        assert self.season.phase == 'Diplomacy'
        for order in self.orders:
            if isinstance(order, Move) and not order.resolved:
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
        province_methods = {Build: self.open_home_centers,
                            Disband: self.occupied_provinces}
        for power in self.powers:
            orders = self.build_orders_of(power)
            if len(orders) == 0:
                continue
            adjustment = type(first(orders))
            provinces = province_methods[adjustment](power)
            # Pick the first valid order for each province.
            valid = []
            for province in provinces:
                valid.append(self.orders.order_in(province, orders=orders))
            for order in orders:
                if order not in valid:
                    order.invalid_action(self.units, self.orders)
                order.resolved = True

    def __execute_diplomacy__(self):
        """ Method to execute successful moves for adjudication of Diplomacy
        phase.

        """
        for order in self.orders:
            if isinstance(order, Move) and order.moves():
                order.unit.move_to(order.target)

    def __execute_retreats__(self):
        """ Method to execute retreats.

        """
        for retreat in self.orders:
            if isinstance(retreat.order, Disband) or retreat.disbands:
                self.delete_unit(retreat.order.unit)
            elif isinstance(retreat.order, Move):
                retreat.unit.move_to(retreat.order.target)

    def __execute_builds__(self):
        """ Method to execute builds.

        """
        for order in self.orders:
            if isinstance(order, Disband):
                self.delete_unit(order.unit)
            if isinstance(order, Build) and order.location is not None:
                self.add_unit(order.force, order.owner, order.location)

    def __unit_counts__(self):
        """ Counts the number of units for each power.
        
        """
        return {power: len(self.units_of(power)) for power in self.powers}

    def __open_home_center_counts__(self):
        """ Counts the number of open home centers for each power.

        """
        return {power: len(self.open_home_centers(power)) for power in self.powers}

    def __setup__(self):
        """ Method to setup the current phase.
        
        """
        if self.season.phase == 'Diplomacy':
            self.orders = DiplomacyOrders(Hold, self.units)
        
        elif self.season.phase == 'Retreats':
            self.orders = RetreatOrders(Retreat, self.orders)
        
        else:
            self.__adjust_supply_centers__()
            self.orders = BuildOrders(
                Build,
                Disband,
                self.supply_centers,
                self.__open_home_center_counts__(),
                self.__unit_counts__()
            )

    def conclude(self, mute, assume=True):
        """ Method to conclude the game if there is a winner.

        """
        if assume:
            assert self.winner is None, 'Game has already concluded.'
        self.winner = next((power for power in self.powers if 
                            (len(self.supply_centers[power]) >= 
                             self.variant.win_condition)), None)
        if self.winner is not None and not mute:
            print(f'Game won by {self.winner.name}.')

    def adjudicate(self, mute=False, verbose=False, hold=False):
        """ Main method to adjudicat the game.

        """
        assert self.winner is None

        # Resolve orders
        getattr(self, f'__resolve_{self.season.phase.lower()}__')(verbose)
        self.__archive_orders__()
        if self.__unresolved_count__() != 0:
            raise AdjudicationError('Resolution ended with unresolved orders.')
        # Execute orders
        getattr(self, f'__execute_{self.season.phase.lower()}__')()
        self.season.progress()  # N.B. this will change the season.phase
        # Setup next phase
        self.__setup__()
        self.conclude(mute)
        self.__archive_position__()
        # If next phase requires no orders, then move on automatically
        if (not hold) and (len(self.orders) == 0) and (self.winner is None):
            self.adjudicate(mute=mute, verbose=verbose)
