#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Unittests for :cls:adjudicator.orders.Hold

The tests should be run from the base directory.
    
"""


import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders import Hold


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.unit = Mock()
        self.unit.location.province = 'Province'
        self.unit.location.__str__ = MagicMock(return_value='Location')
        self.unit.force = 'Army'
        self.unit.owner.genitive = 'Austrian'
        self.unit.sort_string = MagicMock(return_value='sort string')

        self.order = Hold(self.unit)

    def tearDown(self):
        pass

    def test___init___1(self):
        self.assertEqual(
            self.order.unit,
            self.unit
        )

    def test___init___2(self):
        self.assertEqual(
            self.order.province,
            self.unit.location.province
        )

    def test___init___3(self):
        self.assertEqual(
            self.order.max_status.status,
            'valid'
        )

    def test___init___4(self):
        self.assertEqual(
            self.order.min_status.status,
            'illegal'
        )

    def test___init___5(self):
        self.assertFalse(
            self.order.resolved
        )

    def test___init___6(self):
        self.assertEqual(
            self.order.max_hold,
            34
        )

    def test___init___7(self):
        self.assertEqual(
            self.order.min_hold,
            1
        )

    def test___str__(self):
        self.assertEqual(
            self.order.__str__(),
            'Austrian Army in Location holds [unresolved].'
        )

    def test_sort_string(self):
        self.assertEqual(
            self.order.sort_string(),
            'sort string'
        )

    def test_resolved_1(self):
        self.assertFalse(
            self.order.resolved
        )

    def test_resolved_2(self):
        self.order.max_hold = 1
        self.order.min_status = 'valid'

        self.assertTrue(
            self.order.resolved
        )

    def test_resolve(self):
        self.mock = Mock()
        self.mock.aids = MagicMock(return_value=[])
        self.mock.__iter__=MagicMock(return_value=[self.order])
    
        self.order.resolve(None, self.mock)
        self.assertTrue(
            self.order.resolved
        )


if __name__ == '__main__':
    unittest.main()
