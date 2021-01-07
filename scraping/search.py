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

import pandas as pd
import re
import time


# =============================================================================
# Functions to retrieve information form the Beautiful Soup parse search page.
# =============================================================================

def chunks(lst, k):
    """ Splits a list into several lists with k parts.
        
    """
    if len(lst) % k != 0:
        raise ValueError('The list does not split into equal parts.')
    return [lst[i:i + k] for i in range(0, len(lst), k)]


def get_games_players(html):
    """ Retrieves the lists of games and players from a Beautiful soup-parsed 
    search response page from webdiplomacy/vdiplomacy. 
    
    These are retrieved together since their relative position marks which 
    players that played in which games. Due to formatting, winners are listed
    twice. Note that due to replacements, a game may have more than two 
    players.

    """   
    href = [link.get('href') for link in html.find_all('a')]
    href = [link for link in href if isinstance(link, str)
            and (link.startswith('board') or link.startswith('userprofile')
                 or link.startswith('profile'))]
    # Games are links to 'board.php'
    games = [link for link in href if link[0] == 'b']
    game_indices = [i for i, link in enumerate(href) if link[0] == 'b']
    # Extract the list of players for each game
    starting_indices = [k + 1 for k in [-1] + game_indices]
    players = [href[starting_indices[i]: k] for i, k in enumerate(game_indices)]
    return games, players


def get_results(html, powers):
    """ Retrieves the results from a search page in Beautiful soup format, in
    order of appearance.

    """
    # Load relevant em-elements and, make to strings, and remove em-tags
    preliminary = [re.sub(re.compile('<.*?>'), '', str(em)) for em 
                   in html.find_all('em') if not(str(em).startswith('<em '))]
    # Insert marker '0' after each 'Defeated' entry in the list
    defeated = [i for i, prel in enumerate(preliminary) if prel == 'Defeated']
    defeated.reverse()
    for k in defeated:
        preliminary.insert(k+1, '0')
    # Adjust for webDiplomacy bug sometimes not writing out results for bot 
    # games:  insert string 'Drawn' between any two repeated numerical values.
    db_numeric = [i for i, x in enumerate(preliminary) if i > 0 and 
                  (x.isnumeric() and preliminary[i-1].isnumeric())]
    db_numeric.reverse()
    for k in db_numeric:
        preliminary.insert(k, 'Drawn')
    # Extract results; the entries preceeding numerical entries

    results = [preliminary[k-1] for k,x in enumerate(preliminary) 
               if x.isnumeric()]
    supplies = [int(x) for x in preliminary if x.isnumeric()]
    return chunks(results, len(powers)), chunks(supplies, len(powers))


def get_powers(html, powers):
    """ Retrieves the powers playing in games from a search page, in order of 
    apperance. 
    
    Note that, as sets, the ouput is a list a certain number of copies of the 
    parameter _powers_, but the order of the powers represent the order of 
    appearance in the score sheet, which in the end will tell you which power
    won the game.
        
    """
    answer = [re.sub(re.compile('<.*?>'), '', str(span))
              for span in html.find_all('span')
              if str(span).startswith('<span class="country') 
              and len(str(span)) > 37]
    return chunks(answer, len(powers))


def get_pots(html):
    """ Retrieves the pots for the games from a search page, in order of 
    appearance.
    
    """
    # Find all relevant div tags, clear the html tags, and split the strings
    answer = [re.sub(re.compile('<.*?>'), '', str(div)).split()
              for div in html.find_all('div')
              if str(div).startswith('<div class="titleBarLeftSide"><div>')]
    # For each list in answer, pick the numeric elements
    answer = list(map(lambda lst: [x for x in lst if x.isnumeric()], answer))
    # If the game had a pot, then the entry should be a list of length one with
    # the pot as a string. If the game is unranked, then the entry should be an
    # empty list.
    def pot_or_unranked(lst):
        if len(lst) > 0:
            return int(lst[0])
        else:
            return 'Unranked'
    return list(map(pot_or_unranked, answer))


def get_turns(html):
    """ Retrieves the list of on which turns the games on a search place ended.
            
    """
    return [re.sub(re.compile('<.*?>'), '', str(span))
            for span in html.find_all('span')
            if str(span).startswith('<span class="gameDate"')]


def get_phases(html):
    """  Retrieves a list phase lengths for the games from a search page, in 
    order of appearance.
    
    """
    answer = [re.sub(re.compile('<.*?>'), '', str(span))
              for span in html.find_all('span')
              if str(span).startswith('<span class="gameHoursPerPhase"')]
    # Clear ' /phase' ending
    return [string.replace(' /phase', '') for string in answer]


def get_dates(html):
    """ Retrieves the list of IRL end times for the games from a search page,
    in order of appearance
    
    """    
    return [x.get('unixtime') for x in html.find_all('span')
            if x.get('unixtime') is not None]


def is_scoring_system(string):
    """ Returns True if the string is a scoring system.
    
    """
    return string in ['Draw-Size Scoring', 'Unranked',
                      'Sum-of-Squares Scoring', 'Survivors-Win Scoring',
                      'PPSC', 'WTA']

def get_scoring_system(html):
    """ Retrieves the scoring system.
    
    """
    dctnry = {'Draw-Size Scoring': 'DSS', 
              'Unranked': 'Unranked',
              'Sum-of-Squares Scoring': 'SoS',
              'Survivors-Win Scoring': 'PPSC',
              'PPSC': 'PPSC',
              'WTA': 'DSS'}
    lines = [re.sub(re.compile('<.*?>'), '', str(span))
            for span in html.find_all('span')
            if str(span).startswith('<span class="gamePotType">')]
    return [next((dctnry[x] for x in line.split(', ') if is_scoring_system(x)),
                 '')
            for line in lines]

# =============================================================================
# Functions to scrape lists of games form search page.
# =============================================================================

def destring(string):
    if string is None:
        return []
    string = string[1:-1].replace("'", '')
    return string.split(', ')


def ignored_user(users, ignored):
    """ Checks whether one of the users appears in the list list of users.
    
    """
    return any([user in ignored for user in users])
    

def integers(string):
    """ Retrieves the list of integers appearing in a string.
    
    """
    return int(''.join(x for x in string if x.isdigit()))


def game_dcnry(variant, info, game_php, users, powers, pot, results, turn,
               phase, date, supplies, system, page):
    """ Returns a dictionary, which may be inserted into the opening analysis
    dataframe, out of the data representing a game.

    """
    ignored = [int(string) for string in destring(info['Ignore'])]
    # Extract user id's and game id's from unformatted <a href> strings
    user_ids = [integers(string) for string in users]
    user_ids = list(dict.fromkeys(user_ids))  # Delete duplicates in order
    game_id = integers(game_php)
    if ignored_user(user_ids, ignored):
        return None
    dictionary = {'GameID': game_id, 'Page': page, 'Discarded': False, 
                  'Pot': pot, 'Turn': turn, 'Phase': phase, 'Date': date,
                  'ScoringSystem': system}
    # Add entries for scores
    dictionary.update(dict(zip([f'{power}Score' for power in powers],
                               results)))
    dictionary.update(dict(zip([f'{power}Centers' for power in powers],
                               supplies)))
    # Add entrie for user id's
    dictionary.update(dict(zip([f'{power}User' for power in powers],
                               user_ids[:len(powers)])))
    return dictionary


def search_page(variant, k, webpage, info):
    """ Retrieves the data form the k'th search page on the host webpage, and 
    formats it as a dataframe.
    
    """
    name = info[webpage]
    powers = destring(info['Powers'])
    mess_dict = {'All': ('messageNorm=Yes&messagePub=Yes&messageNon=Yes&'
                         'messageRule=Yes'),
                 'Gunboat': ('messageNorm=No&messagePub=No&messageNon=Yes&'
                             'messageRule=No'),
                 'FullPress': ('messageNorm=Yes&messagePub=No&messageNon=No&'
                             'messageRule=Yes')}

    assert info['Messaging'] in mess_dict.keys()
    messaging = mess_dict[info['Messaging']]
    urls = {'webDiplomacy': ('http://webdiplomacy.net/gamelistings.php?gamelis'
                             'tType=Search&status=Finished&userGames=All&seeJo'
                             'inable=All&privacy=All&potType=All&drawVotes=All'
                             f'&variant={name}&excusedTurns=All&anonymity=All&'
                             'phaseLengthMin=All&phaseLengthMax=All&rrMin=All&'
                             f'rrMax=All&betMin=&betMax=&{messaging}&sortCol='
                             'id&sortType=desc&Submit=Search&round=All&pagenum'
                             f'={k}#results'),
            'vDiplomacy': ('https://www.vdiplomacy.com/gamelistings.php?gameli'
                           'stType=Search&status=Finished&userGames=All&seeJoi'
                           'nable=All&privacy=All&potType=All&drawVotes=All&va'
                           f'riant={name}&excusedTurns=All&anonymity=All&phase'
                           'LengthMin=All&phaseLengthMax=All&rrMin=All&rrMax=A'
                           f'll&betMin=&betMax=&{messaging}&sortCol=id&sortTyp'
                           'e=desc&Submit=Search&AllowCookies=Yes&round=All&pa'
                           f'genum={k}#results')}
    try:
        url = urls[webpage]
    except KeyError:
        ValueError('Hosting webpage not recognized.')
    # Beautiful Soup
    search = get(url, stream=True)
    html = BeautifulSoup(search.content, 'html.parser')
    # Retrieve the relevant information
    games, players = get_games_players(html)
    results, supplies = get_results(html, powers)
    powers = get_powers(html, powers)
    pots = get_pots(html)
    turns = get_turns(html)
    phases = get_phases(html)
    dates = get_dates(html)
    system = get_scoring_system(html)
    # Retrieve the entries as dictionaries
    dictionaries = []
    for k, game in enumerate(games):
        dcnry = game_dcnry(variant, info, game, players[k], powers[k], pots[k],
                           results[k], turns[k], phases[k], dates[k], 
                           supplies[k], system[k], webpage)
        if dcnry is not None:
            dictionaries.append(dcnry)
    return dictionaries


def scrape_search_pages(variant, webpage, first, last, wait=3):
    """ Scrapes the lists of games of _variant_ (including all on the search
    page available information) from the host _webpage_, going through from
    search pages no _first_ to _last_. The information is stored in the
    opening analysis csv file of the variant.
    
    Adds an waiting time of _wait_ seconds in between scrapes, for curtesy.
        
    """
    variants = pd.read_csv('data/variants.csv')
    if variant not in list(variants.Name):
        raise ValueError('The variant is not recognized.')
    if webpage not in variants.columns:
        raise ValueError('The hosting webpage is not recognized.')        
    if last < first:
        raise ValueError('Inconsistent page ranges.')
    # Retrieve variant information
    info = variants[variants['Name'] == variant].iloc[0]
    dataset = pd.read_csv(f'data/{variant}.csv')
    for k in range(first, last+1):
        # Function search_page returns a list of dictionaries of games not yet
        # in the database. It should return a dataframe which is to be
        # concatenated.
        dictionaries = search_page(variant, k, webpage, info)
        for dicto in dictionaries:
            if dicto['GameID'] not in list(dataset['GameID']):
                dataset = dataset.append(dicto, ignore_index=True) 
        time.sleep(wait)
    # Save the updated dataset.
    dataset.to_csv(f'data/{variant}.csv', index=False)


