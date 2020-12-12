#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Functions/Mehtods not tested here:
    
    bd.Map.check_consistency()
        Method to check that the information stored in a .json file is ok.

"""
    


# =============================================================================
# Imports
# =============================================================================

import unittest

import adjudicator.board as bd
from adjudicator.auxiliary import *


# =============================================================================
# Tests
# =============================================================================

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map = bd.Map('Classic')
        cls.map.load()
        cls.province = cls.map.provinces[34]
        cls.location = cls.map.locations[28]
        cls.geography = cls.location.geography

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.season = bd.Season('Spring', 'Diplomacy', 1900, count=1)
    
    def tearDown(self):
        pass

    def test_flatten(self):
        answer = flatten([[1], [2, 3], [[4]]])
        self.assertEqual(answer, [1,2,3,[4]])

    def test_despecify(self):
        geo = self.geography
        string = 'Fleet (south coast).'
        self.assertEqual(bd.despecify(string, geo), 'Fleet.')

    def test_first_named(self):
        first = first_named(self.map.provinces, 'Burgundy')
        self.assertEqual(first.name, 'Burgundy')
        self.assertIsInstance(first, bd.Province)
        self.assertFalse(first.supply_center)

    def test_union(self):
        union = dict_union([{1:2}, {3:4}])
        self.assertEqual(union, {1:2, 3:4})

    def test_make_instances(self):
        dicnry = {1: {'name': '10', 'short': '11', 'supply_center': '12'},
                  2: {'name': '20', 'short': '21', 'supply_center': '22'}}
        answer = make_instances(dicnry, bd.Province)
        self.assertEqual(type(answer[0]), bd.Province)
        self.assertEqual(type(answer[1]), bd.Province)
        self.assertEqual(answer[0].name,'10')
        self.assertEqual(answer[1].short,'21')
        self.assertEqual(answer[0].supply_center,'12')



if __name__ == '__main__':
    unittest.main()
