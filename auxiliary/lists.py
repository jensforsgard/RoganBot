#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jensforsgard
"""


def first(list_or_none):
    """ Retrieves the first entry of a list; returns None if the list is
    empty or if the input is not iterable.

    """
    try:
        return list_or_none[0]
    except (TypeError, IndexError):
        return None




def first_named(objects, name):
    """ From a list of objects, return the first object with a given name.

    """
    generator = (obj for obj in objects if obj.name == name)
    return next(generator, None)




def flatten(lists):
    """ Flattens a list of lists on the first level.

    """
    return [item for sublist in lists for item in sublist]




def attr_select(lst, attribute, value=True):
    """ Select objects from a list with a certain value of a certain attribute.
    
    """
    return [obj for obj in lst if getattr(obj, attribute) == value]




def translate(lst, *dicts):
    """ Translates words in a list according to dictionaries; words not
    appearing in the dictionaries are left unalteret.    

    """
    for k, string in enumerate(lst):
        for dctnry in dicts:
            try:
                lst[k] = dctnry[string]
            except KeyError:
                pass

    return lst




def dict_union(dictionary_list):
    """ Joins a list of dictionaries into one dictionary.

    """
    answer = {}
    for entry in dictionary_list:
        answer.update(entry)

    return answer


