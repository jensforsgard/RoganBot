#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 17:53:26 2020

@author: jensforsgard
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
