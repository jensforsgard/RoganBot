#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Unittetst for the classes module.
"""

import unittest

from adjudicator import Map, Province, Season
from lib.classes import make_instances, despecify


class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map = Map('Classic')
        cls.map.load()
        cls.province = cls.map.provinces[34]
        cls.location = cls.map.locations[28]
        cls.geography = cls.location.geography

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.season = Season(1900, 'Spring', 'Diplomacy', count=1)
    
    def tearDown(self):
        pass

    def test_despecify(self):
        geo = self.geography
        string = 'Fleet (south coast).'
        self.assertEqual(despecify(string, geo), 'Fleet.')

    def test_make_instances(self):
        dicnry = {1: {'name': '10', 'short': '11', 'supply_center': '12'},
                  2: {'name': '20', 'short': '21', 'supply_center': '22'}}
        answer = make_instances(dicnry, Province)
        self.assertEqual(type(answer[0]), Province)
        self.assertEqual(type(answer[1]), Province)
        self.assertEqual(answer[0].name,'10')
        self.assertEqual(answer[1].short,'21')
        self.assertEqual(answer[0].supply_center,'12')



if __name__ == '__main__':
    unittest.main()
