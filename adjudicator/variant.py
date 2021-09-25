#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Imports
# =============================================================================

import json

from adjudicator import Map
from lib.classes import make_instances

# =============================================================================
# Error classes
# =============================================================================

class VariantError(Exception):

    def __init__(self, message):

        self.message = message


# =============================================================================
# The Power Class
# =============================================================================

class Power:
    """ This is a class of which an instance is power (or great power),
    partaking in a game.

    Attributes:
        name : string
            The name of the power.
        genetive : string
            The genetive form of the name, for display purpuses.
        home_centers : list of strings
            A list of home center names, recorded as strings.

    """

    def __init__(self, name, dctnry):
        """ The constructor for the Power class.

        Parameters
        ----------
        name : string
        dctnry : dictionary
            A dictionary containing the remaining information.

        """
        self.name = name
        self.genitive = dctnry['genitive']
        self.home_centers = dctnry['home centers']

    def __str__(self, suffix='.'):
        """ Print format.

        """
        return self.name


# =============================================================================
# The Unit Class
# =============================================================================

class Unit:
    """ This is a class of which an instance is unit.

    Attributes:
        id : integer
            The unique id of the unit.
        owner : Power
            The power the unit belongs to.
        force : Force
            The Force instance of the unit.
        specifiers : list of strongs
            A list of the strings of the specifiers which appear in location
            names that may hold the unit's force
        location : Location
            The current location of the unit.
        province : Province
            The Province asociated with the current location of the unit.
    """

    def __init__(self, number, owner, force, location):
        """ The constructor for the unit class.

        Parameters
        ----------
        number : integer
        owner : Power
        force : Force
        location : Location

        """
        self.id = number
        self.owner = owner
        self.force = force
        self.specifiers = force.specifiers
        self.location = location
        self.province = location.province

    def __str__(self, suffix='.'):
        """ Print format.

        """
        assert isinstance(suffix, str)
        return (f'{self.owner.genitive} {self.force.name} in '
                f'{self.location.name}{suffix}')

    def unit_type(self):
        """ Returns the name of the force of the unit.

        """
        return self.force.name

    def move_to(self, location):
        """ Changes the unit's location and province.

        """
        self.location = location
        self.province = location.province

    def sort_string(self):
        """ Returns the string format by which units are sorted.
        
        """
        return f'{self.owner}{self.id}'


# =============================================================================
# The Variant Class
# =============================================================================

class Variant:
    """ This is a class of which an instance is variant of the game.

    Attributes:
        name : string
            The name of the variant.
        powers : list of Powers
            A list of the powers appearing in the variant.
        map : Map
            The map the variant is played on.
        starting_year : integer
            The starting year of the variant.
        starting_positions : dictionary
            A dictionary whose keys are the names of the powers in the game
            and whose values are lists of the starting positions of the units
            of the given powers. Each starting position is itself given as
            a dictionary of a force and a location (given by its name).

    """

    def __init__(self, name):
        """ The constructor for the Variant class.

        Parameters:
        -----------
        name : string
            The name of the variant.

        """
        self.name = name
        self.powers = []
        self.map = None
        self.starting_year = None
        self.starting_positions = []
        self.win_condition = None
        self.unit_colors = None
        self.provinces_colors = None
        self.marker_size = None

    def __str__(self, suffix='.'):
        """ Print format.

        """
        return self.name

    def load(self):
        """ Loads the variant information from the JSON file with the name of
        the variant.

        """
        with open(f'variants/{self.name}.json') as file:
            data = json.load(file)
            file.close()
        assert self.name == data['name']
        self.starting_year = data['starting year']
        self.starting_positions = data['starting positions']
        self.win_condition = data['win condition']
        self.powers = make_instances(data['powers'], Power)
        self.map = Map(data['map'])
        self.map.load()
        self.unit_colors = data['unit colors']
        self.province_colors = data['province colors']
        self.marker_size = data['marker size']


    def instance(self, name, class_type):
        """ Returns the instance of a class with a given name.

        Parameters
        ----------
        name : string
            The name of the instance.
        class_type : type
            The Class the instance belongs to.

        Returns
        -------
        An instance of the class

        """
        # This list should maybe not be hard coded
        classes = {Power: 'powers'}
        try:
            objects = getattr(self, classes[class_type])
        except KeyError:
            objects = getattr(self, class_type)            
        return next((obj for obj in objects if obj.name == name), None)

    def check_consistency(self):
        """ Checks for consistency between powers, units, and the map.

        """
        for power in self.powers:
            power.check_consistency(self.map)
        for unit in self.starting_positions:
            if unit.unit_type not in self.map.units:
                raise VariantError(f'Unit with id {str(unit.id)} is of a type'
                                   ' not recognized by the variant.')
            if unit.owner not in self.powers:
                raise VariantError(f'Unit with id {str(unit.id)} does not '
                                   'belong to one of the recognized powers.')
