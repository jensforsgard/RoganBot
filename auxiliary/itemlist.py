#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This module contains the classes DecoratedItem and ItemList. A decorated
item is an object decorated with an integer. An ItemList is an itarable
collection of decorated items. These appear when scanning a string (i.e., an
order submitted to the game) for objects, when the decoration represents
the position in the string.

Attributes
----------
    DecoratedItem
    ItemList
"""

import re
from auxiliary.errors import OrderInputError


class DecoratedItem:
    """ A item decorated with a position (integer).
    
    """

    def __init__(self, item, number):
        """ Constructor.
        
        """
        self.item = item
        self.position = number


    def __str__(self):
        """ Print method.
        
        """
        return f'{self.item} at {self.position}'


    def translate(self, dictionary):
        """ Translates the item by a dictionary; leaves unaltered if item
        does not appear in the dictionary.
        
        """
        try:
            self.item = dictionary[self.item]
        except KeyError:
            pass




def __appearances__(string, words):
    """ Returns the appearances of words in a string as a (unsorted) list of 
    decorated items.

    """
    string = string.lower()
    answer = []
    for word in words:
        postns = [obj.start() for obj in re.finditer(word.lower(), string)]
        answer += [DecoratedItem(word, pos) for pos in postns if pos > -1]

    return answer




def __first_appearances__(string, words):
    """ Returns the first appearances of words in a string as a (unsorted)
    list of decorated items.

    """
    string = string.lower()
    answer = []
    for word in words:
        pos = string.find(word.lower())
        if pos > -1:
            answer.append(DecoratedItem(word, pos))

    return answer




class ItemList:
    """ An iterable collection of decorated items, initiated from a string
    and a collection of objects.
    
    """

    def __init__(self, string, objects, first=False):
        """ Constructor.
        
        """
        self.words = [str(obj) for obj in objects]
        self.dictionary = dict(zip(self.words, objects))

        if first:
            self.item_list = __first_appearances__(string, self.words)
        else:
            self.item_list = __appearances__(string, self.words)

        for item in self.item_list:
            item.translate(self.dictionary)

        self.__sort__()


    def __str__(self):
        """ Print method.
        
        """
        return '\n'.join([str(item) for item in self.item_list])

    
    def __sort__(self):
        """ Sorts the decorated items by positions.
        
        """
        self.item_list.sort(key=lambda item: item.position)


    def items(self):
        """ Returns the list of items.
        
        """
        return [item.item for item in self.item_list]


    def __iter__(self):
        """ Iterator.
        
        """
        for item in self.items():
            yield item
    
    
    def __len__(self):
        """ Length.
        
        """
        return len(self.item_list)

    
    def loc(self, k, require=True):
        """ Returnes the k'th item.
        
        """
        try:
            return self.item_list[k].item
        except IndexError:
            if require:
                raise OrderInputError(f"Could not find identifier {k+1}.")
            else:
                return None

    
    def pos(self, k, require=True):
        """ Returnes the k'th position.
        
        """
        try:
            return self.item_list[k].position
        except IndexError:
            if require:
                raise OrderInputError(f"Could not find identifier {k+1}.")
            else:
                return None


    def first_after(self, k):
        """ Returns the first item with position at least k
        
        """
        return next((item.item for item in self.item_list 
                     if item.position >= k), None)
