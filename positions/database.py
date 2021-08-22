#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Imports
# =============================================================================

import pandas as pd

from positions.parser import GameFile
from adjudicator.variant import Variant


# =============================================================================
# Class
# =============================================================================

class PositionsDB():
    """ An instance stores and loads information about positions that has
    occurred in a game, into a pandas dataframe.
    
    Parameters are expected to be added, as this class is used in the
    future.

    """

    def __init__(self, variant, folder, host, cols=None):
        """ Constructor.

        """
        self.variant = Variant(variant)
        self.variant.load()
        self.folder = folder
        self.host = host
        self.powers = [power.name for power in self.variant.powers]
        self.data = pd.read_csv(f'scraping/data/{folder}.csv', index_col = 'GameID')
        self.__clean_data__(cols)

    def __clean_data__(self, cols):
        """ Cleans the data loaded from the scraping-folder, removing
        unnecessary columns and discarded games. Also adds the 'Loaded'
        column.
        
        """
        self.data = self.data[~self.data.Discarded]
        if cols is None:
            ENDINGS = ['S1', 'RS1', 'A1', 'RA1', 'W1', 'User']
            cols = [power + end for power in self.powers for end in ENDINGS]
            cols += ['Page', 'Manual', 'Discarded']
        self.data = self.data.drop(cols, axis=1)
        self.data['Loaded'] = False

    def load_centers(self, bound=None):
        """ Loads games, plays them through until the end, and records what
        power owned what center in the dataframe.
        
        """
        j = 1
        for k in self.data.index[~self.data.Loaded]:
            game = GameFile(self.variant.name, self.folder, self.host, str(k))
            game.run()
            centers = game.game.current_position()['centers']
            for key in centers:
            	self.data.loc[k, centers[key]] = key
            self.data.loc[k, 'Loaded'] = True
            if bound is not None:
                if j >= bound:
                    break
            j += 1
    
    def save_csv(self):
        """ Saves the dataframe as a csv file in the sub data folder.
        
        """
        self.data.to_csv(f'positions/data/{self.folder}.csv')
    
    def load_csv(self):
        """ Loads the dataframe from a csv file int he sub data folder.
        This overwrites any changes stored in the current dataframe.
        
        """
        self.data = pd.read_csv(f'positions/data/{self.folder}.csv', index_col = 'GameID')

