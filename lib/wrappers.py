#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This module contains decorators common for other modules.

"""

from adjudicator import Unit


def require(func):
    """ Throws an error if an output is required but not generated.

    """
    def wrapper(*args, **kwargs):
        require = False
        if 'require' in kwargs:
            require = kwargs['require']
            del kwargs['require']
        value = func(*args, **kwargs)
        if require and value is None:
            raise ValueError("Output requested but 'None' obtained.")
        return value
    return wrapper


def pregame(func):
    """ Asserts that we are in apregame phase.
    
    """
    def wrapper(*args, **kwargs):
        message = 'The method can only be called during pregame.'
        assert args[0].season.phase == 'Pregame', message
        return func(*args, **kwargs)
    return wrapper


def builds(func):
    """ Asserts that we are in apregame phase.
    
    """
    def wrapper(*args, **kwargs):
        message = 'The method can only be called during build phase.'
        assert args[0].season.phase == 'Builds', message
        return func(*args, **kwargs)
    return wrapper


def province_or_unit(func):
    """ Translated province_or_unit to unit.
    
    """
    def wrapper(*args, **kwargs):
        game = args[0]
        entry = args[1]
        if game.season.phase == 'Builds':
            assert isinstance(entry, Unit)
        # Adjust for input format.
        if not isinstance(entry, Unit):
            entry = game.unit_in(game.__province__(entry))
        # Delete the unit and its order.
        if not isinstance(entry, Unit):
            raise ValueError('Could not identify the unit to be removed.')
        return func(game, entry, *args[2:], **kwargs)
    return wrapper
