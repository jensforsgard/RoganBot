#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This module contains classes for archiving orders and positions within
games.

"""


class Archive:
    """ An Archive is a collection of entries, stored in a list.

    """

    def __init__(self):
        """ Constructor.
 
        """
        self.entries = []

    def reset(self):
        """ Method to reset to an empty archive.
        
        """
        self.entries = []

    def __iter__(self):
        """ Iterator.
        
        """
        for item in self.entries():
            yield item

    def __len__(self):
        """ Length.
        
        """
        return len(self.entries)

    def loc(self, k):
        """ Retrieves the kth entry.
        
        """
        return self.entries[k]

    def last(self):
        """ Retrieves the last entry.
        
        """
        return self.loc(-1)
    
    def rollback(self):
        """ Rollsback one turn.
        
        """
        del self.entries[-1]


class OrderArchive(Archive):
    """ An OrderArchive is a collection of order lists, stored as lists of
    strings.
    
    """

    def __str__(self, k=None):
        """ Print method.
        
        """
        if k is None:
            return str(self.entries)
        else:
            return str(self.loc(k))

    def enter(self, game):
        """ Enters the current order list into the archive.
        
        """
        entry = [str(order) for order in game.orders].copy()
        entry.sort()
        self.entries.append(entry)


class PositionArchive(Archive):
    """ A PositionArchive is a collection of positions, stored as dictionaries
    of strings.
    
    """

    def __str__(self, k=None):
        """ Print method.
        
        """
        if k is None:
            return str(self.entries)
        else:
            return str(self.loc(k))

    def enter(self, game):
        """ Enters dictionary with the game's current position into the archive.

        """
        dcnry = {'season': game.season.name,
                 'phase': game.season.phase,
                 'year': game.season.year,
                 'units': [{'force': str(unit.force), 'power': str(unit.owner),
                            'location': unit.location.id} for unit in game.units],
                 'centers': {str(power): [str(province) for province in
                                          game.supply_centers[power]]
                             for power in game.powers}}
        self.entries.append(dcnry)

    def centers(self, game):
        """ Returns the dictionary of supply centers with all entries into
        classes.
        
        """
        dcnry = self.last()['centers']
        return {game.variant.instance(key, 'powers'):
                set(game.variant.map.instances(dcnry[key], 'provinces'))
                for key in dcnry}

    def units(self):
        """ Returns the list of units in the last entry of the archive.

        """
        return self.last()['units']

    def setup(self, game):
        """ Setup the game according to the last entry in the archive.
        
        """
        game.supply_centers = self.centers(game)
        game.units = []
        game.orders = []
        for entry in self.units():
            game.add_unit(**entry, overrule=True)
