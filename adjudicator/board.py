"""
@author: jensforsgard
"""

import json

#from adjudicator.auxiliary import *
from lib.errors import MapError
from lib.lists import (flatten, first_named, attr_select, dict_union)
from lib.classes import (despecify, make_instances, dict_string)

from adjudicator import (Force, Geography, Location, Province)



class Map:
    """ A game map.

    Attributes:
        name: string
            Identifies the JSON file form which we'll load information.
        forces: list of forces
            Allowed forces.
        orders: list of strings
            Allowed orders.
        geographies: list of Geographies
        provinces: list of Provinces
        locations: list of Locatinos
        force_dict: dictionary
            A dictionary with short forms of geography specifiers.
        prov_dict: dictionary
            A dictionary of short forms of province names.
        supply_centers: list of Provinces
            A list of the supply centers provinces.
        loaded: boolean
            Whether the map has been loaded or not.

    """

    def __init__(self, name):
        """ Constructor.

        """
        self.name = name
        self.loaded = False

    def __str__(self):
        """ Print format.

        """
        return self.name

    # def __loaded__(func):
    #     """ Wrapper function that test if a map object has been loaded. Only
    #         necessary if a map object is accessed on its own.

    #     """
    #     def wrapper(*args, **kwargs):
            
    #         try:
    #             if not args[0].loaded:
    #                 raise MapError('Map has not been loaded.')
        
    #         except AttributeError:
    #             raise TypeError(f'{args[0]} cannot be marked as loaded.')
        
    #         return func(*args, **kwargs)
        
    #     return wrapper

#    @__loaded__
    def info(self, string):
        """ Retrieves information as a string.

        """
        lower = string.lower()
        if lower == 'provinces':
            return str([province.name for province in self.provinces])
        elif lower == 'supply centers':
            return str([province.name for province in self.supply_centers])
        elif lower == 'abbreviations':
            return dict_string(self.prov_dict)
        raise ValueError(f'Cannot display {string}.')

    def display(self, string):
        """ Prints some entities associated to the map.

        """
        print(self.info(string))

    def load(self):
        """ Loads the map information from the JSON file in the maps folder.

        """
        with open(f'maps/{self.name}.json') as file:
            data = json.load(file)
        assert self.name == data['name']  # Check that the file is not corrupt

        self.orders = tuple(data['orders'])

        # Create all class instances
        self.forces = make_instances(data['forces'], Force)
        self.provinces = make_instances(data['provinces'], Province)
        self.geographies = make_instances(data['geographies'], Geography, map=self)
        self.locations = make_instances(data['locations'], Location, map=self)

        # Retrieve the short form dictionaries.
        self.force_dict = dict_union([fce.short_forms for fce in self.forces])
        self.prov_dict = {prv.short: f'{prv.name}' for prv in self.provinces}

        # Retrieve the list of supply centers.
        self.supply_centers = tuple(attr_select(self.provinces,
                                                'supply_center'))

        self.loaded = True
    
    	### Should check consistencies; that the index of a location is
    	### equal to its position in the self.locations list.
    
    def instance(self, name, class_):
        """ Finds the instance of a given class with a given name.

        """
        # This list should maybe not be hard coded...
        attributes = {Force: 'forces',
                      Geography: 'geographies',
                      Province: 'provinces'}
        try:
            objects = getattr(self, attributes[class_])
        except KeyError:
            objects = getattr(self, class_)            
        return next((obj for obj in objects if obj.name == name), None)

    def instances(self, lst, class_):
        """ Finds instances of a given class with given names.
        
        """
        return [self.instance(name, class_) for name in lst]

#    @__loaded__
    def locations_of(self, province):
        """ Returns all locations attached to a given province.

        """
        return attr_select(self.locations, 'province', province)

#    @__loaded__ 
    def locate(self, force, name, origin=None, specifier=None, either=False):
        """ Returns a location identified by partial data.

        Parameters
        ----------
        force: Force
        name: string or integer
        origin: Location, optional
        specifier: string, optional
        either: boolean
            Whether an ambiguous return is allowed.

        """
        if type(name) in (str, Province):
            locations = [location for location in self.locations
                         if location.named(str(name)) and location.force == force]
            # Filter by reachable from origin location
            if len(locations) >= 2 and origin is not None:
                locations = [location for location in locations
                             if origin.id in location.connections]
            # Filter by specifier.
            if len(locations) >= 2 and specifier is not None:
                locations = [location for location in locations
                             if location.name == f'{name} {specifier}']
        else:            
            locations = [location for location in self.locations
                         if location.id == name]
        if len(locations) > 1 and not either:
            raise MapError(f'There are at least two locations in {name} '
                           'matching the given criteria.')
        try:
            return locations[0]
        except IndexError:
            return None  # No available location.

#    @__loaded__
    def one_adjacent(self, locations, province):
        """ Tests if one location from a list of locations is adjacent to
        one location associated to a given province.
        
        """
        return next((True for location in locations
                     if location.reaches_province(province)),
                    False)

#    @__loaded__
    def has_path(self, source, target, via):
        """ Tests if there is a path from a source to target provinces via a
        set of given locations. N.B., it *does not* suffice that source is
        adjacent to the target.

        """
        # The first step is special because we're checking adjacency to the
        # source province, and not the other locations.
        new = [location for location in via
               if location.reaches_province(source)]
        reached = new.copy()
        arrived = self.one_adjacent(reached, target)

        while not arrived and len(new) > 0:
            ids = flatten([location.connections for location in reached])
            # Find the newly reached locations in this step.
            new = [location for location in via if location.id in ids 
                   and location not in reached]
            arrived = self.one_adjacent(new, target)
            reached = reached + new

        return arrived
