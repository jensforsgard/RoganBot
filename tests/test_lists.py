#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Unittests for the list module.
"""

import unittest
import adjudicator.board as bd
from lib.lists import (first, first_named, flatten, attr_select,
                       translate, dict_union)


class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map = bd.Map('Classic')
        cls.map.load()
        cls.location = cls.map.locations[28]
        cls.geography = cls.location.geography

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.season = bd.Season('Spring', 'Diplomacy', 1900, count=1)
    
    def tearDown(self):
        pass



    def test_first(self):
        self.assertEqual(first([0,1]), 0)
        self.assertEqual(first([]), None)

    def test_first_named(self):
        first = first_named(self.map.provinces, 'Burgundy')
        self.assertEqual(first.name, 'Burgundy')
        self.assertIsInstance(first, bd.Province)
        self.assertFalse(first.supply_center)

    def test_flatten(self):
        answer = flatten([[1], [2, 3], [[4]]])
        self.assertEqual(answer, [1,2,3,[4]])

    def test_attr_select(self):
        lst = attr_select(self.map.provinces, 'supply_center')
        self.assertEqual(len(lst), 34)

    def test_translate(self):
        lst = translate([1,2,3,4], {2:5, 4:2})
        self.assertEqual(lst, [1,5,3,2])

    def test_dict_union(self):
        lst = [{1:2}, {3:4}]
        dcnry = dict_union(lst)
        self.assertEqual(dcnry[1], 2)
        self.assertEqual(dcnry[3], 4)

if __name__ == '__main__':
    unittest.main()
