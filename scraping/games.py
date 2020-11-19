#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 22:43:37 2020

@author: RoganJosh
"""

# =============================================================================
# Imports
# =============================================================================

from requests import get
from bs4 import BeautifulSoup
from search import destring
import pandas as pd
import numpy as np
import re
import time
import os
import itertools
import json

# =============================================================================
# Auxiliary functions 
# =============================================================================

def try_int(string):
    try:
        return int(string)
    except ValueError:
        return None


# =============================================================================
# Scraping game html files
# =============================================================================

def scrape_game(game, variant, page):
    """ Retrieves the html file with all orders for the game, and stores it in
    the folder associated with the variant.

    Currently, identifiers between pages are not overlapping, and this should
    not be a problem for a long time. But, at some point, these files should be
    stored in folders that are host-specific.
    
    """    
    if page not in ['webDiplomacy', 'vDiplomacy']:
        raise ValueError('Hosting webpage not recognized.')
    urls = {'webDiplomacy': (f'http://webdiplomacy.net/board.php?gameID={game}'
                             '&viewArchive=Orders'),
            'vDiplomacy': (f'https://www.vdiplomacy.com/board.php?gameID='
                           f'{game}&viewArchive=Orders')}
    webpage = get(urls[page], stream=True)
    file = open(f'data/games/{variant}/{page}/{game}.html', 'w')
    file.write(str(webpage.content))
    file.close()


def scrape_games(variant, page, wait=3, m=100, verbose=True):
    """ Scrapes games of form a specific page in a specific variant.

    """
    df = pd.read_csv(f'data/{variant}.csv')
    df = df[(df.Discarded == False) & (df.Page == page)]
    want = list(df.GameID);
    exist = [try_int(string.replace('.html','')) 
             for string in os.listdir(f'data/games/{variant}/{page}')]
    missing = [k for k in want if k not in exist]
    if verbose:
        print(f'{len(want)} games of {variant} from {page} in the database.\n'
              f'{len(missing)} remains to be scraped.\n'
              f'{min([m, len(missing)])} will be scraped in this batch.')
    for i in range(min(m, len(missing))):
        scrape_game(missing[i], variant, page)
        time.sleep(wait)

# =============================================================================
# 
# =============================================================================

def extract_game_powers(html, m=2):
    """ Retrieves the powers from a game html file in the order they appear in
    terms of order display.
    
    The parameter m is the number of players in the variant.
    
    """     
    powers = [re.sub(re.compile('<.*?>'), '', str(span)) 
              for span in html.find_all('span') 
              if str(span).startswith('<span class="country')]
    return powers[-m:]


def equal_orders(list1, list2):
    """ Determines if two lists of lists of orders are equal.
    
    """
    return np.all([set(list1[k]) == set(list2[k]) for k in range(len(list1))])

def adjust_phases(orders, m=2, last=False):
    for k in range(m):
        if orders[1 + 3*k][0] != 'Retreats':
            orders.insert(1 + 3*k, ['Retreats'])
        if orders[2 + 3*k][0] != 'Unit-placement':
            orders.insert(2 + 3*k, ['Unit-placement'])
    for k in range(m-1):
        if orders[1 + 3*m + 2*k][0] != 'Retreats':
            orders.insert(1 + 3*m + 2*k, ['Retreats'])
    if len(orders) == 5*m - 1:
        orders.insert(5*m - 1, ['Retreats'])
    prefix = [order[0] for order in orders]
    if prefix.count('Retreats') != 2*m:
        return []
    elif prefix.count('Unit-placement') != m:
        return []
    # This code assumes that m=2; Should not be a problem since this code is
    # not used when creating an opening database
    if last and (equal_orders(orders[0:2], orders[6:8]) 
                 and equal_orders(orders[3:5], orders[8:10])):
        orders[0] = ['Diplomacy']
        orders[1] = ['Retreats']
        orders[2] = ['Unit-placement']
        orders[3] = ['Diplomacy']
        orders[4] = ['Retreats']
        orders[5] = ['Unit-placement']
    return orders


def format_one_year(entries, m=2, last=False):
    phases = [k for k, entry in enumerate(entries) 
              if entry in ['Diplomacy', 'Retreats','Unit-placement']]
    # Append the index for the (last+1)st phase
    phases.append(len(entries))
    # Split the entries vector into subvectors according to power and phase
    orders = [entries[x: phases[k+1]] for k, x in enumerate(phases)
              if k < len(phases) - 1]
    # Loop to add any missing phases (must be looped since expected location
    # assumes all previous phases are there).
    orders = adjust_phases(orders, m, last)
    return orders


def extract_orders(html, year, m=2):
    """ Retrieves the orders for a specified year from a game html file.
    
    The parameter m is the number of player in the variant.
    
    """     
    entries = [re.sub(re.compile('<.*?>'), '', str(li))
               for li in html.find_all('li')]
    # Find the location of diplomacy phases
    dip_phases = [k for k, entry in enumerate(entries)if entry == 'Diplomacy']
    # Append the index for the (last+1)st phase
    dip_phases.append(len(entries))
    # Find the beginning and end indices of the interesting phases
    start = dip_phases[-2*m*year - 1]
    end = dip_phases[-2*m*(year-1) - 1]
    # Filter the relevant entries
    entries = entries[start:end]
    # Find location of all phases in the filtered vector
    orders = format_one_year(entries, m=m)
    # Return the list where we drop the first entry of each element
    return list(map(lambda x: x[1:], orders))


def translate_order_list(orders, territories):
    """ Takes a list of orders and translates to the short standard form
    according to dictionary.
    
    """
    shorts = {'(fail)': '', '(dislodged)': '', '.': '', 'fleet': 'F',
              'army': 'A', 'Do not use build orders': 'wait', 'Build': '',
              '(South Coast)': '(s)', '(West Coast)': '(w)', 
              '(East Coast)': '(e)', '(North coast)': '(n)', 
              'support move to': 'S', 'support hold to': 'S',  'from': '<',
              'hold': 'H', 'move to': '-',
              'via convoy': '', 'convoy to': 'C', 'retreat to': '-',
              'The ': '', 'at ': '', '  ': ' '}
    # Read in the list of province abbreviations
    try:
        with open(f'abbreviations/{territories}.json', 'r') as file:
            abbrvtns = json.load(file)
    except FileNotFoundError:
        abbrvtns = {}
    # Replace all of the territory names
    for key, value in abbrvtns.items():
        orders = [string.replace(key,value) for string in orders]
    for key, value in shorts.items():
        orders = [string.replace(key,value) for string in orders]
    # Sort the anwser before returning
    return sorted(orders)


def game_year_dictionary(gameID, variant, host, year, territories, m=2):
    """ Loads a game file and makes a dictionary containing all lists of 
    orders from the game for a specified year.    
    
    """
    # Read in the game file...
    file = open(f'data/games/{variant}/{host}/{gameID}.html', 'r')
    content = file.read()
    file.close()
    # ...and parse by Beautiful soup
    html = BeautifulSoup(content, 'html.parser')
    # Retrieve the information of which powers are playing
    powers = extract_game_powers(html, m)
    # Construct the list of lists of orders in their translated standard form
    orders = [translate_order_list(ord_list, territories)
              for ord_list in extract_orders(html, year, m)]
    # Construct the list of seasons
    autumn = [[f'{power}A{year}', f'{power}RA{year}', f'{power}W{year}']
              for power in powers]
    spring = [[f'{power}S{year}', f'{power}RS{year}'] for power in powers]
    seasons = list(itertools.chain(*autumn)) + list(itertools.chain(*spring))
    # Construct the dictionary by paring orders with seasons assuming at least
    # one order, and return
    return {seasons[k]: orders[k] for k in list(range(len(seasons)))
            if len(orders[k]) > 0}


def load_year(year, variant, host, variants, m=1000):
    """ Loads k'th year of all scraped games into the csv file
        
    """    
    # Retrieve one column key for moves for first year, in order to have a
    # column to check for content to exlude files that has already been read
    # into the .csv file
    powers = destring(variants[variants.Name == variant].Powers.iloc[0])
    territories = variants[variants.Name == variant].Dictionary.iloc[0]
    col1 = f'{powers[0]}S{year}'
    df = pd.read_csv(f'data/{variant}.csv')
    unloaded = df[(df[col1].isnull()) & (df['Discarded']==False)
                  & (df['Manual']==False)].copy()
    existing = [try_int(string.replace('.html','')) for string 
                in os.listdir(f'data/games/{variant}/{host}/')]
    load = [i for i in unloaded.index 
            if unloaded.loc[i, 'GameID'] in existing]
    print(f'There are {len(load)} games left to import.')
    for i in load[:m]:
        dictionary = game_year_dictionary(unloaded.loc[i, 'GameID'], variant,
                                          host, year, territories, m=len(powers))
        for key in dictionary.keys():
            df[key].loc[i] = dictionary[key]
    df.to_csv(f'data/{variant}.csv', index=False)

    