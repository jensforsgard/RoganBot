#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This module contains error classes.

"""

class MapError(Exception):

    def __init__(self, message):
        self.message = message


class AdjudicationError(Exception):

    def __init__(self, message):
        self.message = message


class GameError(Exception):

    def __init__(self, message):
        self.message = message


class OrderInputError(Exception):

    def __init__(self, message):
        self.message = message


class PuzzleError(Exception):

    def __init__(self, message):
        self.message = message

class ParserError(Exception):

    def __init__(self, message):
        self.message = message


# class OrderError(Exception):

#     def __init__(self, message):
#         self.message = message
