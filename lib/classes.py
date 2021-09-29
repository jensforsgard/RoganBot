#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This module contains minor functions for object manipulation and
information extraction.

"""

from yaml import load, Loader


with open('adjudicator/config.yaml', 'r') as file:
    RELEVANCE = load(file, Loader)['relevance']


def despecify(string, geography):
    """ Removes the specifiers of the geography from the string.

    """
    for specifier in geography.force.specifiers:
        string = string.replace(f' {specifier}', '')
    
    return string


def make_instances(dctnry, class_, *args, **kwargs):
    """ Creates a tuple of instances of a class whose identifiers are the
    keys of the dictionary and properties are given by the values of the
    dictionary.

    """
    
    # This line should be depricated.
    try:
        return tuple([class_(key, dctnry[key], *args, **kwargs) for key in dctnry])
     
    except TypeError:
        return tuple([class_(key, **{**dctnry[key], **kwargs}) for key in dctnry])


def dict_string(dctnry, deliminator='', func=lambda x: x):
    """ Returns a string of a dict of objects with __str__ methods.
    
    """
    strings = {}
    for key in dctnry:
        if type(dctnry[key]) == str:
            strings[key] = func(dctnry[key])
        else:
            try:
                strings[key] = set(map(str, map(func, dctnry[key])))
            except TypeError:
                strings[key] = str(func(dctnry[key]))
    return '\n'.join([f'{key}{deliminator} {strings[key]}' for key in dctnry])


def isorderinstance(order, string):
    """ Tests if an order is of a given instance.
    
    """
    return order.relevance == RELEVANCE[string.lower()]

def orders_of_type(orders, string):
    """ Filters a list of order by type.

    """
    return [order for order in orders if isorderinstance(order, string)]
