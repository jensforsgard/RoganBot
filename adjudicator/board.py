#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jensforsgard
"""




import json

#from adjudicator.auxiliary import *
from auxiliary.errors import MapError
from auxiliary.lists import (flatten, first_named, attr_select, dict_union)
from auxiliary.classes import (despecify, make_instances, dict_string)



class Province:
    """ A province is a ion of the map. 

    Attributes:
        id: integer
            Should be unique; is used as secondary identifier.
        name: string
            Sould be unique; is used as primary identifyer.
        short: string
            A three letter abbreviation of the name.
        supply_center: boolean
            Whether the province contains a supply center or not.

    """



    def __init__(self, idn, dcnry):
        """ Constructor.
        
        Parameters
        ----------
        idn: integer
            The id number of the province.
        dctnry: dictionary
            A dictionary encoding the remaining properties.

        """
        self.id = int(idn)
        for key in dcnry:
            setattr(self, key, dcnry[key])



    def __str__(self):
        """ Print format.

        """
        return self.name




class Geography:
    """ A Geography is a container of a unit associated with a province.

    Attributes:
        name: string
            Should be unique; primary identifier for geographies.
        force: Force
            Only units of this force may be contained in the geography.
        orders: list of strings
            The type of orders, encoded by their names, which are available
            for a unit contained in an instance of the geography.

    """



    def __init__(self, name, dctnry, map_):
        """ Constructor.

        Parameters
        ----------
        name: string
        dctnry: dictionary
            Containing the remaining properties.
        map_: Map
            The game map, necessary to initate the force attribute.
        """
        self.name = name
        self.force = map_.instance(dctnry['unit'], Force)
        self.orders = dctnry['orders']



    def __str__(self):
        """ Print format.

        """
        return self.name




class Location:
    """ A location is a geography attached to a province.
    
    The location specifies adjacent (i.e., reachable) locations.

    Attributes:
        id: integer
            Should be unique; is used as primary identifier.
        name: string
            Not necessarily unique.
        geography: Geography
        force: Force
            Same as the force of the geography.
        province: Province
        connections: list of integers
            A list of all adjacent locations encoded by their ids.

    """



    def __init__(self, idn, dctnry, map_):
        """ Constructor.

        Parameters
        ----------
        idn: integer
            The id of the location.
        dctnry: dictionary
            Containing the remaining defining properties.
        map_: Map
            The game map, necessary to initate the geography and the
            province attributes.

        """

        self.id = int(idn)
        self.name = dctnry['name']
        self.connections = tuple(dctnry['connections'])

        self.geography = map_.instance(dctnry['geography'], Geography)
        self.force = self.geography.force

        province_name = despecify(self.name, self.geography)
        self.province = first_named(map_.provinces, province_name)



    def __str__(self):
        """ Print format.

        """
        return self.name
    
    

    def reaches_location(self, location):
        """ Tests if the instance reaches a given location.

        """
        try:
            return location.id in self.connections

        except AttributeError:
            return location in self.connections



    def reaches_province(self, map_, province):
        """ Tests if the instance reaches any location associated to a given
        province. Needs the map to determine all locations of the province.

        """
        ids = [location.id for location in map_.locations_of(province)]
        return next((True for nr in ids if nr in self.connections), False)



    def named(self, name):
        """ Tests if the instance is associated with the given name.

        """
        return self.name == name or self.province.name == name




class Force:
    """ A Force is a type of unit.
    
    Attributes:
        name: string
        may_receive: list of strings
            List of orders, as strings, which the force may be object of.
        specifiers: list of strings
            List of specifiers of locations that can contain the force.
        short_forms: dictionary
            Short forms of the specifiers.

    """



    def __init__(self, name, dctnry):
        """ Constructor.

        """
        self.name = name
        self.may_receive = tuple(dctnry['may receive'])
        self.specifiers = tuple(dctnry['specifiers'])
        self.short_forms = dict(zip(dctnry['short forms'], self.specifiers))



    def __str__(self):
        """ Print format.

        """
        return self.name




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
    def info(self, string, require=False):
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
        self.geographies = make_instances(data['geographies'], Geography, self)
        self.locations = make_instances(data['locations'], Location, self)

        # Retrieve the short form dictionaries.
        self.force_dict = dict_union([fce.short_forms for fce in self.forces])
        self.prov_dict = {prv.short: f'{prv.name}' for prv in self.provinces}

        # Retrieve the list of supply centers.
        self.supply_centers = tuple(attr_select(self.provinces,
                                                'supply_center'))

        self.loaded = True


    
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
        """ Tests if one location from a list of locaions is adjacent to
        one location associated to a given province.
        
        """
        return next((True for location in locations
                     if location.reaches_province(self, province)),
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
               if location.reaches_province(self, source)]
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




class Season:
    """ The class that keeps track of the season of the game.

    Attributes:
        name: string
        phase: string
            The name of the phase.
        year: integer
        count: integer
            The order of the season.

    """



    def __init__(self, name, phase, year, count=0):
        """ Constructor.

        """
        self.count = count
        self.name = name
        self.phase = phase
        self.year = year



    def __str__(self):
        if self.phase == 'Pregame':
            return 'Pregame.'
        elif self.phase == 'Builds':
            return f'Builds in {str(self.year)}.'
        else:
            return f'{self.phase} in {self.name} {str(self.year)}.'



    def __set_name_phase__(self):
        """ Deduces name and phase from the count.

        """
        k = self.count % 5

        if k in [1, 3]:
            self.phase = 'Diplomacy'
        elif k in [2, 4]:
            self.phase = 'Retreats'
        else:
            self.phase = 'Builds'
        
        if k in [1, 2]:
            self.name = 'Spring'
        else:
            self.name = 'Fall'



    def progress(self):
        """ Moves the season forward one phase.

        """
        self.year += (self.phase == 'Builds')
        self.count += 1
        self.__set_name_phase__()



    def relapse(self):
        """ Moves the season backwards one phase. 
        
        """
        assert self.count > 1, ('Cannot relapse to before starting season.')
        self.count -= 1
        self.__set_name_phase__()
        self.year -= (self.phase == 'Builds')



    def conclude(self):
        self.phase = 'Postgame'
        self.name = '-'
        self.count += 1

