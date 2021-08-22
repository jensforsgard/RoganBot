#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The parser module contains the GameFile class.
# An instance of the GameFile class loads a scraped html file,
# and can plays through the full game using the orders found
# in the file.

# =============================================================================
# Imports
# =============================================================================

import re

from bs4 import BeautifulSoup

from lib.lists import flatten, split_at
from adjudicator.game import Game
from adjudicator.orders import Build, Disband


# =============================================================================
# Class
# =============================================================================

class GameFile():
    """ A GameFile contains the information stored in a html file
    scraped from webDiplomacy or vDiplomacy, together with methods
    used to play through the full game.

    """

    def __init__(self, variant, folder, host, identifier):
        """ Constructor.

        Parameters
        ----------
        variant: string
        	map name, as stored in the adjudicator/variants folder.
        folder: string
            The name of variant in the variants.csv table
        host: string
            The name of the host webpage
        identifier: string
            The unique identifier of the game.

        """
        self.game = Game(variant)
        self.game.start()
        self.folder = folder
        self.host = host
        self.identifier = identifier
        self.ended = False
        with open(f'scraping/data/games/{folder}/{host}/{identifier}.html', 'r') as file:
            self.html = BeautifulSoup(file.read(), 'html.parser')
        self.powers = [power.name for power in self.game.variant.powers]
        self.order_types = ['Diplomacy', 'Retreats', 'Unit-placement']
        self.extract_orders()
#        self.adjust()

    def order_entries(self):
        """ Retrieves the list of order entries from the html file.
        
        """
        return [re.sub(re.compile('<.*?>'), '', str(li))
                for li in self.html.find_all('li')]

    def count_orders(self, info):
        """ Counts the number of order sets that belongs to teach
        Diplomacy + Retreat + Builds sequence, using _info_.
        
        """
        indices = [k for k, entry in enumerate(info) 
                   if entry not in (self.order_types + self.powers)]
        indices.append(len(info))
        self.order_counts = {info[indices[k]]: indices[k+1] - indices[k] - 1
                             for k in range(len(indices) - 1)}

    def insert_orders(self, key, collections):
        """ Inserts orders at key in self.orders.
        
        """
        self.orders[key] = {ot: [] for ot in self.order_types}
        for entry in collections:
            self.orders[key][entry[0]] += [string.replace('St.', 'Saint')
                                           for string in entry[1:]]

    def split_orders(self, orders):
        """ Splits a sequence of orders based on order_type entries.
        
        """
        indices = [k for k, entry in enumerate(orders) if entry in self.order_types]
        indices.append(len(orders))
        return [orders[indices[k]:indices[k+1]] for k in range(len(indices) - 1)]

    def dict_comparison(self, dict1, dict2):
        """ True if values of dictionaries are equal as sets.
        
        """
        for entry in self.order_types:
            if set(dict1[entry]) != set(dict2[entry]):
                return False
        return True

    def check_duplicated_last(self):
        """ Checks whether the last season's orders where dumped twice;
        adjusts for a webDip bug.
        
        """
        keys = list(self.orders.keys())
        if self.dict_comparison(self.orders[keys[0]], self.orders[keys[1]]):
            del self.orders[keys[0]]

    def extract_orders(self):
        """ Extracts the orders from the html file.
        
        """
        entries = self.order_entries()
        info, orders = split_at(entries, 'Spring, 1901', shift=len(self.powers)+1)
        self.count_orders(info)
        orders = self.split_orders(orders)
        self.orders = {}
        for key, value in self.order_counts.items():
            self.insert_orders(key.replace('Autumn', 'Fall'),
                               orders[:value])
            del orders[:value]
        self.check_duplicated_last()

    def adjudicate(self, k=1):
        """ Method to adjudicate k seasons. Delegates depending
        on the season.
        
        """
        name = self.game.season.name + ', ' + str(self.game.season.year)
        try:
            getattr(self, f'adjudicate_{self.game.season.phase}')(self.orders[name])
        except KeyError:
            self.ended = True

    def adjudicate_Diplomacy(self, orders):
        """ Method to adjudicate a Diplomacy season.
        
        """
        self.game.order(orders['Diplomacy'])
        self.game.adjudicate(mute=True)

    def adjudicate_Retreats(self, orders):
        """ Method to adjudicate a Retreat season.
        
        """
        self.game.order(orders['Retreats'])
        self.game.adjudicate(mute=True)

    def next_placement_order_of(self, power, orders):
        """ Pops the next placement order in one of the centers.
        
        """
        relevant = [center.name for center in self.game.supply_centers[power]
                    if center.name in power.home_centers]
        for k, item in enumerate(orders['Unit-placement']):
            for center in relevant:
                if center in item:
                    return orders['Unit-placement'].pop(k)

    def next_disband_order_in(self, centers, orders):
        """ Pops the next placement order in one of the centers.
        
        """
        for k, item in enumerate(orders['Unit-placement']):
            for center in centers:
                if center in item:
                    return orders['Unit-placement'].pop(k)

    def adjudicate_Builds(self, orders):
        """ Method to adjudicate a Build season.
        
        """
        for order in self.game.orders:
            if isinstance(order, Build):
                string = self.next_placement_order_of(order.owner, orders)
            if isinstance(order, Disband):
                units = [unit.province.name for unit in self.game.units_of(order.owner)]
                string = self.next_disband_order_in(units, orders)
            if string is not None:
                self.game.order(f'{order.id} {order.owner.name} {string}')
        self.game.adjudicate(mute=True)

    def run(self):
        """ Method to adjudicate until the game is over.
        
        """
        while (not self.ended) and self.game.winner is None:
            self.adjudicate()
        # Adjust for old webDip bug
        if self.game.season.phase == 'Retreats':
            self.game.adjudicate(mute=True)
