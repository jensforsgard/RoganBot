#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jensforsgard
"""


import re

from adjudicator.errors import OrderInputError





def flatten(lists):
    """ Flattens a list of lists on the first level.

    """
    return [item for sublist in lists for item in sublist]




def despecify(string, geography):
    """ Removes the specifiers of the geography from the string.

    """
    for specifier in geography.force.specifiers:
        string = string.replace(f' {specifier}', '')
    
    return string




def first_named(objects, name):
    """ From a list of objects, return the first object with a given name.

    """
    generator = (obj for obj in objects if obj.name == name)
    return next(generator, None)




def dict_union(dictionary_list):
    """ Joins a list of dictionaries into one dictionary.

    """
    answer = {}
    for entry in dictionary_list:
        answer.update(entry)

    return answer




def make_instances(dictnry, class_, *args):
    """ Creates a tuple of instances of a class whose identifiers are the
    keys of the dictionary and properties are given by the values of the
    dictionary.

    """
    return tuple([class_(key, dictnry[key], *args) for key in dictnry])



def attr_select(lst, attribute, value=True):
    """ Select objects from a list with a certain value of a certain attribute.
    
    """
    return [obj for obj in lst if getattr(obj, attribute) == value]



def appearances(objects, string, first=False, require=0, label=True):
    """ Returns the appearances of objects in a string. Default output is a
    list of dictionaries with 'entry' and 'position', sorted by
    positions. 

    Parameters
    ----------
    objects: list
    string: string
    first: boolean, optional
        If True, then only the first appearance of each object is returned.
    require: integer, optional
        If required a number of total appearances. If not met, an 
        OrderInputError is raised.
    label: boolena, optional
        If False, the output is a list of objects in order of appearance.

    """
    answer = []
    for entity in objects:

        try:  # Retrieve the name of the object if possible.
            word = entity.name.lower()
        except AttributeError:
            word = str(entity).lower()

        if first:
            postns = [string.lower().find(word)]
        else:
            postns = [obj.start() for obj in re.finditer(word, string.lower())]

        answer += [{'entry': entity, 'position': entry} for entry in postns
                   if entry > -1]

    if len(answer) < require:
        raise OrderInputError(f'Could not find the required number ({require})'
                              f' of objects in the string {string}.')

    answer.sort(key=lambda entry: entry['position'])

    if not label:
        return [position['entry'] for position in answer]

    return answer




def translate(lst, dictionary):
    """ Translates words in a list according to a dictionary; words not
    appearing in the dictionary are left unalteret.    

    """
    for k, string in enumerate(lst):

        try:
            lst[k] = dictionary[string]
        except KeyError:
            pass

    return lst
    


def first(list_or_none):
    """ Retrieves the first entry of a list; returns None if the list is
    empty or if the input is not iterable.

    """
    try:
        return list_or_none[0]
    except (TypeError, IndexError):
        return None
