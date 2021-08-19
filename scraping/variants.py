#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 23:09:28 2020

@author: jensforsgard
"""

# =============================================================================
# Imports
# =============================================================================

import pandas as pd
import os


# =============================================================================
# Global parameters.
# =============================================================================

folder = 'scraping/data'


# =============================================================================
# Adding a new variant.
# =============================================================================

def dataset_columns(powers, seasons):
    """ Returns the list of columns for the opening analysis dataframe.
            
    """    
    # Common columns
    columns = ['GameID', 'Pot', 'Page', 'Discarded', 'Phase', 'Turn', 'Date',
               'Manual', 'ScoringSystem']
    # Power dependent columns
    columns.extend([power + suff for power in powers 
                    for suff in ['Score', 'User', 'Centers']])
    # Power and season dependent columns
    columns.extend([power + midfix + str(k+1) for power in powers 
                    for midfix in ['S', 'RS', 'A', 'RA', 'W'] 
                    for k in list(range(seasons))])
    return columns


def add_variant(name, powers, years=2, overwrite=False):
    """ Creates the necessary infrasticture to conduct an opening analysis of
    the variant calle _name_. That is, creates a row in the variants.csv
    DataFrame, creates a new DataFrame for storing games, and creates a folder
    for scraped game files.

    Parameters
    ----------
    name: str
    powers: list of strings
        The names of the powers in the variant.
    years: int, optional
        The number of years included in the opening analysis. The default is 2.
    overwrite: boolean, optional
        Whether possibly existing DataFrames should be overwritten.

    """
    variants =  pd.read_csv(f'{folder}/variants.csv')
    if name in list(variants['Name']):
        if overwrite:
            variants = variants[variants['Name'] != name]
        else:
            raise ValueError('There is already a variant with the given name.')
    # Append a row to variants.csv
    variants = variants.append({'Name': name, 'Powers': powers,
                                'Ignore': '[]'}, ignore_index=True)
    variants.to_csv(f'{folder}/variants.csv', index=False)
    # Create and save the opening analysis dataframe.
    dataset = pd.DataFrame(columns=dataset_columns(powers, years))
    dataset.to_csv(f'{folder}/{name}.csv', index=False)
    # Create folder for scraped game files.
    paths = [f'{folder}/games/{name}', 
             f'{folder}/games/{name}/webDiplomacy',
             f'{folder}/games/{name}/vDiplomacy']
    for path in paths:
        if not(os.path.isdir(path)):
            os.mkdir(path)

