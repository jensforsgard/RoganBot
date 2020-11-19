#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 23:09:28 2020

@author: jensforsgard
"""

# =============================================================================
# Imports
# =============================================================================

import pandas   as pd
import re

from bs4 import BeautifulSoup


# =============================================================================
# Cleaning; before scraping game files.
# =============================================================================

def discard_short_games(variant, length, dataframe):
    """ Flips the 'Discarded' entry to 'True' for games which ended within the
    first _length_ in-game years in the opening analysis dataframe.
    
    The starting year is retrieved from the dataframe passed on.
        
    """
    
    row = dataframe[dataframe.Name == variant]
    assert len(row) == 1, KeyError('Dataframe contains two variants with the '
                                   'same name.')
    try:
        year = int(row.Start.iloc[0])
    except ValueError:
        raise ValueError('Variant does not have valid starting year.')
    games = pd.read_csv(f'data/{variant}.csv')
    def extract_year(turn):
        turn = turn.replace('Spring, ', '')
        turn = turn.replace('Autumn, ', '')
        return int(turn)
    bools = [extract_year(turn) < int(year) + length for turn in games.Turn] 
    games.update(pd.DataFrame({'Discarded': bools}))
    games.to_csv(f'data/{variant}.csv', index=False)


def discard_game(nr, variant):
    """ Flips the 'Discarded' entry to 'True' for games which ended within the
    first _length_ in-game years in the opening analysis dataframe.
    
    The starting year is retrieved from the dataframe passed on.
        
    """

    games = pd.read_csv(f'data/{variant}.csv')
    for col in games.columns:
        if col not in ['GameID', 'Pot', 'Page', 'Discarded', 'Phase', 'Turn',
                       'Date', 'Manual']:
            games.loc[nr, col] = None
    games.loc[nr, 'Discarded'] = True
    games.to_csv(f'data/{variant}.csv', index=False)

# =============================================================================
# Clearning, after scraping game files.
# =============================================================================

def first_season(gameID, variant, host='vDiplomacy'):
    """ Finds the first season recorded in the html-file for game with the
    given id in the game folder.
        
    """
    
    # Read the game html file from the folder andr parse through Beautiful soup
    file = open(f'data/games/{variant}/{host}/{gameID}.html', 'r')
    content = file.read()
    file.close()
    html = BeautifulSoup(content, 'html.parser')

    # Pull the last <h4> tag and clear off the html code
    season = str(re.sub(re.compile('<.*?>'), '', str(html.find_all('h4')[-1])))

    # Return the string after clearing off excess characters
    return season.replace('\\', '').replace('tt','').replace(' rnt:','')


def manuals(variant, var_df):
    """ Turns 'Manual' entry to 'True' for games in opening ananlysis dataframe
    which are from vDiplomacy and had too many seasons played. Here, df is the
    dataframe with variant information.
    
    """
    # Load the variant start year 
    year = int(var_df.loc[var_df.Name==variant, 'Start'].iloc[0])    
    if year is None:
        raise ValueError('Warning: find_manual_games: No such variant')
    # Load the variant dataframe
    df = pd.read_csv(f'data/{variant}.csv')    
    for k in df.index:
        if df.loc[k, 'Page'] != 'vDiplomacy':
            df.loc[k, 'Manual'] = False
        elif df.loc[k, 'Discarded']:
            df.loc[k, 'Manual'] = False
        elif first_season(df.loc[k, 'GameID'], variant) == 'Spring, 1901':
            df.loc[k, 'Manual'] = False
        else:
            df.loc[k, 'Manual'] = True
    df.to_csv(f'data/{variant}.csv', index = False)
