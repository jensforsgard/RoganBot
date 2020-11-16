#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# =============================================================================
# Imports
# =============================================================================

import adjudicator.orders as od
import adjudicator.variant as vr
import adjudicator.board as bd
import re
import geopandas as geo
import os
import matplotlib.pyplot as plt
from shapely.geometry import Polygon


# =============================================================================
# Functions
# =============================================================================

def appearances(objects, string, first=False, require=0, label=True):
    """ Returns the appearances of objects in a string.  By default, the output
    is a list of dictionaries with keys 'entry' and 'position', sorted by
    positions. If the 'label' flag is turned off, the output is a list of all
    appearances, sorted by order of appearance. If the first flag is turned on,
    the output includes only the first appearance of _each_ object. A required
    number of total appearances might be requested, in which case the function
    will throw an OrderInputError if the requirement is not met.

    Parameters
    ----------
    objects: list
        List of objects of some class.
    string: string
    first: boolean, optional
        Whether to return first isntances or all instances.
        The default is False.
    require: integer, optional
        The number of required instances.
    label: boolena, optional
        Whether to return a dictionary with instances and positions, or a
        list of instances ordered by positions.

    Raises
    ------
    OrderInputError
        If there is fewer entries than the required number.

    Returns
    -------
    answer: dictionary or list.

    """
    answer = []
    for entity in objects:
        try:  # Retrieve the name of the object if possible.
            word = entity.name.lower()
        except AttributeError:
            word = str(entity).lower()
        if first:
            postns = [string.lower().find(word)]
        else:
            postns = [obj.start() for obj in re.finditer(word, string.lower())]
        answer = answer + [{'entry': entity, 'position': entry} 
                           for entry in postns]
    # Must sort before we can discard the 'position' value
    answer = [ans for ans in answer if ans['position'] > -1]
    if len(answer) < require:
        raise OrderInputError(f'Could not find the required number ({require})'
                              f' of objects in the string {string}.')
    answer.sort(key=lambda entry: entry['position'])
    if not label:
        answer = [position['entry'] for position in answer]
    return answer


def translate(lst, dictionary):
    """ Translates words in a list according to a dictionary; words not
    appearing in the dictionary are left unalteret.    

    """
    for k, string in enumerate(lst):
        try:
            lst[k] = dictionary[string]
        except KeyError:
            pass
    return lst
    

def first(list_or_none):
    """ Retrieves the first entry of a list; returns None if the list is
    empty or if the input is not iterable.

    """
    try:
        return list_or_none[0]
    except (TypeError, IndexError):
        return None


# =============================================================================
# Error classes
# =============================================================================

class AdjudicationError(Exception):

    def __init__(self, message):
        self.message = message


class GameError(Exception):

    def __init__(self, message):
        self.message = message


class OrderInputError(Exception):

    def __init__(self, message):
        self.message = message


# =============================================================================
# Game Class
# =============================================================================

class Game:
    """ A game of Diplomacy.

    Attributes:
        page : string or None
            Name of the webpage hosting the game, None if no host
        identifier : string or None
            Identifier of the game at the host webpage, None if no page.
        variant : Variant
            The variant of the game.
        season : Season
            The current season of the game.
        powers : list of Powers
            List of the powers playing in the game.
        forces : list of Forces
            List of forces included in the game.
        units : list of Units
            List of current units in the game.
        provinces : list of Provinces
            List of provinces of the map.
        home_centers : dictionary
            Dictionary whose keys are the powers and whose values are lists of
            provinces making out the home centers of the power in question.
        supply_centers : dictionary
            Dictionary whose keys are the powers and whose values are lists of
            provinces making out the currently owned supply centers of the
            power in question.
        orders : list of orders
            List of orders for the units in the game in the current phase.
        winner : Power or None
            The winner of the game, or None if no winner has been determined.
        position_archive : list
            List of all previous positions that occured in the game.
        order_archive : list
            List of all final order sets submitted to the game for each phase.
        graphics : geopandas GeoDataFrame
            graphical information to plot the game
        shift : float
            The shift in position applied in various plotting features. Depends
            on the projection of the map.

    """

    orders_dict = {'-': 'move', 'S': 'support', 'C': 'convoy', 'H': 'hold',
                   'B': 'build', 'D': 'disband', 'R': 'retreat',
                   'A': 'army', 'F': 'fleet', 'St': 'Saint', 
                   'destroy': 'disband'}

    def __init__(self, variant_name, page=None, identifier=None):
        """ The constructor for the game class.

        Parameters
        ----------
        variant_name : string
            The name of the variant to be played.
        page : string, optional
            The name of the webpage where the game is/was played.
        identifier : string, optional
            The identifier of the game at the webpage.

        """
        self.page = page
        self.identifier = identifier
        self.variant = vr.Variant(variant_name)
        self.variant.load()
        self.season = bd.Season('Spring', 'Pregame',
                                self.variant.starting_year)
        self.powers = self.variant.powers
        self.forces = self.variant.map.forces
        self.units = []
        self.provinces = self.variant.map.provinces
        self.home_centers = {}  # These will be loaded once the game begins
        self.supply_centers = {}
        self.orders = []
        self.winner = None
        self.position_archive = []
        self.order_archive = []
        self.graphics = None
        self.shift = None

    # =========================================================================
    # Methods to print and archive information
    # =========================================================================

    def __str__(self):
        """ Print method.

        """
        return (f'Game variant: {self.variant.name}.\n'
                f'Game map: {self.variant.map.name}.\n'
                f'Season: {self.season.__str__()}')

    def info(self, string='units', number=-1):
        """ Print method.

        """
        options = ['abbreviations', 'archive', 'center counts', 'centers', 
                   'map', 'units', 'variant', 'orders', 'options', 'position',
                   'provinces', 'season', 'supply centers']
        if string not in options:
            print('Option not recognized.')
            return
        elif string == 'options':
            print(options)
        elif string == 'variant':
            print(self.variant)
        elif string == 'map':
            print(self.variant.map)
        elif string == 'season':
            print(self.season)
        elif string == 'position':
            self.show()
        elif string == 'abbreviations':
            for key in self.orders_dict.keys():
                print(f'{key}   {self.orders_dict[key]}')
            self.variant.map.display('abbreviations')
        elif string in ['provinces', 'supply centers']:
            self.variant.map.display(string)
        elif self.season.phase == 'Pregame':
            raise GameError('Display option not available in Pregame phase.')
        elif string == 'centers':
            for power in self.powers:
                provinces = [prov.name for prov in self.supply_centers[power]]
                print(f'{power.name}: {provinces}')
        elif string == 'center counts':
            print({power.name: len(self.supply_centers[power]) 
                   for power in self.powers})
        elif string in ['units', 'orders']:
            self.__sort_units__()
            self.__sort_orders__()
            objects = getattr(self, string)
            for obj in objects:
                print(obj)
        elif string == 'archive':
            for entry in self.order_archive[number]:
                print(entry)


    def current_position(self):
        """ Returns a dictionary with a copy of the game's current position.

        """
        dcnry = {'season': self.season.name, 'phase': self.season.phase}
        units = {unit.location.name: f'{unit.owner.name} {unit.force.name}'
                 for unit in self.units}
        dcnry.update(units)
        n_units = {f'{power.name}Units': len(self.units_of(power)) 
                   for power in self.powers}
        dcnry.update(n_units)
        for power in self.powers:
            dcnry.update({prov.name + '_sc': power.name
                          for prov in self.supply_centers[power]})
        n_centers = {f'{power.name}Centers': len(self.supply_centers[power])
                     for power in self.powers}
        dcnry.update(n_centers)
        return dcnry

    def __archive_position__(self):
        """ Archives the current position.

        """
        self.position_archive.append(self.current_position())

    def __archive_orders__(self):
        """ Archives the current set of orders.

        """
        self.__sort_orders__()
        entry = [str(order) for order in self.orders]
        self.order_archive.append(entry.copy())

    def __unit_color__(self, power):
        """ Returns the color the unit should be given when plotted.

        """
        return self.variant.unit_colors[power.name]

    def __province_color__(self, province_or_name):
        """ Returns the color the province should be given in a plot of the
        current position of the game.

        """
        try:
            name = province_or_name.name
        except AttributeError:
            name = province_or_name
        dcnry = self.variant.province_colors
        if name in [prov.name for prov in self.variant.map.supply_centers]:
            color = 'snow'
        else:
            color = 'oldlace'
        if self.season.phase != 'Pregame':
            for power in self.powers:
                supp = [prov.name for prov in self.supply_centers[power]]
                if name in supp:
                    color = dcnry[power.name]
        return color

    def __plot_province__(self, index, gdf):
        """ Returns a plt.fill of province of the given index of the geodataframe.

        """
        geom = gdf.loc[index, 'geometry']
        # Load the colors.
        if gdf.loc[index, 'land'] == False:
            color = 'azure'
            edgecolor = 'cornflowerblue'
        elif gdf.loc[index, 'static']:
            color = 'lightgray'
            edgecolor = 'black'
        else:
            color = self.__province_color__(gdf.loc[index, 'name'])
            edgecolor = 'black'
            # Plot
        if type(geom) == Polygon:
            plt.fill(*geom.exterior.xy, facecolor=color, 
                     edgecolor=edgecolor, linewidth=.3)
        else:
            for poly in geom:
                plt.fill(*poly.exterior.xy, facecolor=color, 
                         edgecolor=edgecolor, linewidth=.3)

    def __plot_unit__(self, unit, gdf, retreat=False):
        """ Returns a plt.plot of the units current location.

        """
        markers = {'Army': 'o', 'Fleet': '^'}
        color = self.__unit_color__(unit.owner)
        point = gdf[gdf.name == unit.location.name].iloc[0].geometry
        size = self.variant.marker_size
        if retreat:
            plt.plot([point.x + self.shift], [point.y - self.shift], 
                     marker=markers[unit.force.name],
                     color=color, markersize=.75*size,
                     markeredgewidth=.3, markeredgecolor='red')
        else:
            plt.plot([point.x], [point.y], marker=markers[unit.force.name],
                     color=color, markersize=size,
                     markeredgewidth=.3, markeredgecolor='black')
            

    def show(self):
        """ Plots the current position. 

        """
        if self.graphics is None:
            self.load_graphics()
        gdf = self.graphics
        plt.figure(dpi=150)
        plt.axis('off')
        plt.margins(0)
        # Plot the provinces
        sea = gdf[(gdf.point == False) & (gdf.land == False)]
        land = gdf[(gdf.point == False) & (gdf.land == True)]
        for k in sea.index:
            self.__plot_province__(k, sea)
        for k in land.index:
            self.__plot_province__(k, land)
        # Plot the units
        points = gdf[(gdf.point == True) & (gdf.text == False)]
        if self.season.phase == 'Retreats':
            retreats = [order.unit for order in self.orders]
        else:
            retreats = []
        units = [unit for unit in self.units if unit not in retreats]
        for unit in retreats:
            self.__plot_unit__(unit, points, True)
        for unit in units:
            self.__plot_unit__(unit, points)
        # Plot names of provinces
        points = gdf[(gdf.point == True) & (gdf.text == True)]
        for k in points.index:
            point = points.loc[k, 'geometry']
            plt.annotate(points.loc[k, 'name'], xy=(point.x, point.y))
        plt.show()

    # =========================================================================
    #  Methods to start the game
    # =========================================================================

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
            # Using that home centers are the supply centers holding a unit
            # at the beginning of the game.
            self.supply_centers[power] = set(self.occupied_provinces(power))
            self.home_centers[power] = self.supply_centers[power].copy()
        self.__archive_position__()

    def reset(self):
        """ Resets the game to Pregame settings.

        """
        self.season = bd.Season('Spring', 'Pregame', 
                                self.variant.starting_year)
        self.units = []
        self.supply_centers = {}
        self.home_centers = {}
        self.orders = []
        self.winner = None
        self.position_archive = []
        self.order_archive = []

    def rollback(self):
        """ Rolls back the game one turn. 
        
        It does so by playing through the order archive. This is suboptimal,
        but the adjudicator is sufficiently fast for this not to be a problem.

        """
        archive = self.order_archive.copy()
        while archive[-1] == []:
            del archive[-1]
        self.reset()
        self.start()
        for j, orders in enumerate(archive):
            if orders != []:
                self.order(orders)
                if j + 1 != len(archive):
                    self.adjudicate()

    def load_graphics(self):
        """ Loads the GeoDataFrame from the 

        """
        path = f'graphics/{self.variant.map.name}.geojson'
        if os.path.isfile(path):
            self.graphics = geo.read_file(path)
            self.graphics.to_crs('ESRI:54027', inplace=True)
        else:
            raise GameError('No graphics file found.')
        ycoords = [point.y for point in 
                   self.graphics[self.graphics.point == True].geometry]
        self.shift = (max(ycoords) - min(ycoords))*.01

    # =========================================================================
    #  Methods to sort
    # =========================================================================

    def __sort_units__(self):
        """ Sorts the list of units according to owner and unit id.

        """
        self.units.sort(key=lambda unit: f'{unit.owner.name}{unit.id}')

    def __sort_orders__(self):
        """ Sorts the list of orders.

        """
        if self.season.phase == 'Builds':
            self.orders.sort(key=lambda order: f'{order.owner.name}{order.id}')
        else:
            self.orders.sort(key=lambda order: (f'{order.unit.owner.name}'
                                                '{order.unit.id}'))

    def __sort_by_relevance__(self):
        """ Sorts the list of orders by order type; for a faster adjudication
        procedure.

        """
        self.orders.sort(key=lambda order: order.relevance)

    # =========================================================================
    # Methods to retrieve basic information.
    # =========================================================================

    def unit_in(self, province, require=False):
        """ Retrieves the unit in a province. Throws and error if an output is
        required but no unit can be identified.

        Parameters:
        -----------
        province: Province
        require: boolean, optional
            Encodes whether an output is required. Default is False.

        """
        assert self.season.phase != 'Retreats'
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
        assert self.season.phase != 'Builds'
        generator = (order for order in self.orders if order.unit is unit)
        return next(generator, None)

    def order_in(self, province, require=False, orders=None):
        """ Retrieves the order of a unit in a province. Throws an error if
        an order is required but not available. You may restrict the search
        to a specific set of orders.

        Parameters
        ----------
        province: Province
        require: boolean, optional
            Whether a not None output is required. The default is False.
        orders: list, optional
            List of orders in which the order should be contained. If value
            is None, then it uses self.orders. The default is None.

        Raises
        ------
        OrderInputError
            In case there is no output but an output is required.

        Returns
        -------
        answer: order

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

        Parameters
        ----------
        number : integer
        power : Power
        require : boolean, optional

        Raises
        ------
        OrderInputError
            In case output is required but not present.

        Returns
        -------
        order : order

        """
        assert self.season.phase == 'Builds'
        if type(power)is not str:
            power = power.name
        generator = (order for order in self.orders
                     if order.id == number and order.owner.name is power)
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

    # =========================================================================
    # Methods to retrieve information from partial data
    # =========================================================================

    def instance(self, name, class_or_class_name, require=False):
        """ Returns an instance of a class identified by its name.

        Parameters
        ----------
        name : string
        class_or_class_name : string of class
        require : boolena, optional

        Raises
        ------
        GameError
            If an output is required bu not present.

        Returns
        -------
        answer : class instance

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

        Parameters
        ----------
        force : Force
        name : string
        origin : Location or None, optional
        specifier : string or None, optional
        require : boolean, optional

        Raises
        ------
        GameError
            If an output is required but not present.

        Returns
        -------
        location : Location or None

        """
        location = self.variant.map.locate(force, name, origin, specifier,
                                           either)
        if require and location is None:
            raise GameError(f'Could not locate {force.name} in {name}.')
        return location

    # =========================================================================
    # Methods to retrieve processed information.
    # =========================================================================

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

    # =========================================================================
    # Methods to update information and/or edit the game
    # =========================================================================

    def add_unit(self, force, owner, location):
        """ Adds a unit to the game in a given location. If we are in the
        Diplomacy phase, a standard order is also added.

        Parameters
        ----------
        force : Force or force name.
        owner : Power or power name.
        location : Location or location name.

        """
        assert self.season.phase != 'Retreats'
        # Retrieve classes if input was strings.
        if not isinstance(force, bd.Force):
            force = self.instance(force, bd.Force, require=True)
        if not isinstance(owner, vr.Power):
            owner = self.instance(owner, vr.Power, require=True)
        if not isinstance(location, bd.Location):
            location = self.locate(force, location, require=True)
        # Check that the given location is available.
        if not self.unit_in(location.province) is None:
            raise GameError('Named province already contains a unit.')
        unit = vr.Unit(self.__next_unit_id__(), owner, force, location)
        self.units.append(unit)
        if self.season.phase == 'Diplomacy':
            self.orders.append(od.Hold(unit))

    def delete_unit(self, province_or_unit):
        """ Deletes a unit from the game.

        Parameters
        ----------
        province_or_unit: Unit, Province, or name of a Province

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
        self.units = [entry for entry in self.units if entry is not unit]
        self.orders = [ordr for ordr in self.orders if ordr.unit is not unit]

    def __update_order__(self, order, old=None):
        """ Replaces an old order with a new order. If the order is given
        during the Diplomacy phase, the the old order is identified by the
        unit. During other phases, you may specify the order to be replaced.

        Parameters
        ----------
        order: Diplomacy_Order
        old: Diplomacy_Order, optional

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

    # =========================================================================
    # Methods for order input
    # =========================================================================

    def __format__(self, string):
        """ Takes a string input form a user and adjusta to a format assumed
        by the formatting methods. Also replaces abbreviations with their
        full lenght counterparts.

        """
        string = string.replace('.', '')
        words = [word for word in string.split(' ') if len(word) > 0]
        # The first dictionary should perhaps not be hard-corded
        words = translate(words, self.orders_dict)
        words = translate(words, self.variant.map.province_dict)
        words = translate(words, self.variant.map.forces_dict)
        return ' '.join(words).lower()

    def order(self, string_or_list):
        """  Accepts a string or a list of strings as input. Passes on the 
        adjusted lists of words to the phase specific input methods.

        """
        phase = self.season.phase
        if phase not in ['Diplomacy', 'Retreats', 'Builds']:
            print('No orders expected for the current phase.')
        elif type(string_or_list) is list:
            for string in string_or_list:
                self.order(string)
        else:
            adjusted = self.__format__(string_or_list)
            getattr(self, f'__input_{phase.lower()}__')(adjusted)

    def __format_move__(self, text, named_orders):
        """ Formats a move order from a string.

        """
        provinces = appearances(self.provinces, text, True, 2)
        source = provinces[0]
        unit = self.unit_in(source['entry'], True)
        # Determining the location in the target province.
        province = provinces[1]['entry']
        text = text[source['position']:]
        specifier = first(appearances(unit.specifiers, text, True, 0, False))
        target = self.locate(unit.force, province.name,
                             unit.location, specifier, True)
        # Checking if convoy
        convoy = 'Convoy' in named_orders
        # Might be that the order should be accepted but failed at resolution.
        if convoy and 'Convoy' not in unit.force.may_receive:
            raise OrderInputError(f'{text}: Unit may not be convoyed.')
        return od.Move(unit, convoy, target)

    def __format_hold__(self, text, named_orders):
        """ Formats a hold order from a string.

        """
        province = first(appearances(self.provinces, text, True, 1, False))
        unit = self.unit_in(province, True)
        return od.Hold(unit)

    def __format_support__(self, text, named_orders):
        """ Formats a support order from a string.

        """
        if len(named_orders) < 2:
            raise OrderInputError(f'{text}: Support with missing object order.')
        # N.B. referring to the __format_hold__ method would be slower.
        if named_orders[1] == 'Hold':
            provinces = appearances(self.provinces, text, True, 2, False)
            unit = self.unit_in(provinces[0], True)
            ob_unit = self.unit_in(provinces[1], True)
            return od.Support(unit, od.Hold(ob_unit))
        # Due to the webDiplomacy reverse input format, referring to the
        # __format_move__ method is not possible.
        elif named_orders[1] == 'Move':
            flipped = text.find(' from ') > -1
            # Checking provinces and units.
            provinces = appearances(self.provinces, text, True, 3)
            unit = self.unit_in(provinces[0]['entry'], True)
            source = provinces[1 + int(flipped)]
            ob_unit = self.unit_in(source['entry'], True)
            target_prov = provinces[2 - int(flipped)]
            # Determining the location in the target province.
            if flipped:
                subtext = text[target_prov['position']:source['position']]
            else:
                subtext = text[target_prov['position']:]
            spec = first(appearances(unit.specifiers, subtext, True, 0, False))
            province_name = target_prov['entry'].name
            target = self.locate(ob_unit.force, province_name,
                                 ob_unit.location, spec, True, True)
            # Return
            return od.Support(unit, od.Move(ob_unit, False, target))
        else:
            raise OrderInputError(f'{text}: Supported order may not receive support.')

    def __format_convoy__(self, text, named_orders):
        """ Formats a convoy order from a string.

        """
        named_provinces = appearances(self.provinces, text, True, 3, False)
        unit = self.unit_in(named_provinces[0], True)
        flipped = text.find(' from ') > -1
        object_unit = self.unit_in(named_provinces[1 + int(flipped)], True)
        target = named_provinces[2 - int(flipped)]
        if 'Convoy' not in unit.location.geography.orders:
            raise OrderInputError(f'{text}: Fleet in coast may not convoy.')
        if 'Convoy' not in object_unit.force.may_receive:
            raise OrderInputError(f'{text}: Object unit may not be convoyed.')
        # Possible error if new forces are introduced: In the current variants,
        # only Armies may be convoyed,
        target = self.locate(object_unit.force, target.name, require=True)
        return od.Convoy(unit, od.Move(object_unit, True, target))

    def __input_diplomacy__(self, string):
        """ Method to input orders during the Diplomacy phase. Identifies the
        class of the order and calls the corresponding class specific
        formatting method.

        """
        orders = appearances(self.variant.map.orders, string, True, 1, False)
        order_class = orders[0].lower()
        order = getattr(self, f'__format_{order_class}__')(string, orders)
        self.__update_order__(order)

    def __input_retreats__(self, text):
        """ Method to input orders during the Retreat phase.

        """
        labelled_provinces = appearances(self.provinces, text, True, 1)
        province = labelled_provinces[0]['entry']
        old = self.order_in(province, True)
        unit = old.unit
        if len(labelled_provinces) == 1:  # interpret as a disband order.
            new = od.Disband(old.id, unit.owner, unit)
        else:  # interpret as a retreat order.
            target_prov = labelled_provinces[1]
            subtext = text[target_prov['position']:]
            spec = first(appearances(unit.specifiers, subtext, True, 0, False))
            name = target_prov['entry'].name
            target = self.locate(unit.force, name, unit.location, spec, True)
            new = od.Move(unit, False, target)
        retreat = od.Retreat(old.id, unit, new, old.forbidden)
        self.__update_order__(retreat, old)

    def __input_builds__(self, text):
        """ Method to input orders during the Build phase.

        """
        number = first(appearances(range(9), text, True, 1, False))
        names = [power.name for power in self.powers]
        power = first(appearances(names, text, True, 1, False))
        old = self.adjustment_order(number, power, True)
        if (text.find(' postpone ') > -1 or text.find(' default ') > -1 
            or text.find(' do not use ') > -1):
            if isinstance(old, od.Disband):
                new = od.Disband(old.id, old.owner, None)
            elif isinstance(old, od.Build):
                new = od.Build(old.id, old.owner, None, None)
        else:
            province = first(appearances(self.provinces, text, True, 1, False))
            if isinstance(old, od.Disband):
                unit = self.unit_in(province, True)
                assert unit.owner is old.owner
                new = od.Disband(old.id, old.owner, unit)
            elif isinstance(old, od.Build):
                force = first(appearances(self.forces, text, True, 1, False))
                specifier = first(appearances(force.specifiers, text,
                                              True, 0, False))
                if specifier is not None:
                    location_name = province.name + ' ' + specifier
                else:
                    location_name = province.name
                location = self.locate(force, location_name, require=True)
                new = od.Build(old.id, old.owner, force, location)
        self.__update_order__(new, old)

    # =========================================================================
    # Methods for the adjudication process
    # =========================================================================

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

        Parameters
        ----------
        conclude : boolean, optional
            Whether the game should be concluded if a power reaches the win
            conditions. Might wanna set ot false if the bot is playing for
            prectice. The default is True.

        Raises
        ------
        AdjudicationError
            In case not all orders are resolved.

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
        if self.season.phase != 'Retreats':
            self.__archive_position__()
        # If following phase requires no orders, then move on automatically
        if len(self.orders) == 0 and self.winner is None:
            self.adjudicate(conclude=conclude, mute=mute)
