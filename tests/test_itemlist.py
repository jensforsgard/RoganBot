#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Unittests for the itemlist module.
"""

import unittest
import adjudicator.game as gm

from auxiliary.itemlist import (__first_appearances__, __appearances__, 
                                DecoratedItem, ItemList)
from auxiliary.errors import OrderInputError


class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = gm.Game('Classic')
        cls.game.start()

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_DecoratedItem_translate(self):
        item = DecoratedItem(1, 2)
        item.translate({1: 3})
        self.assertEqual(item.item, 3)
        item = DecoratedItem(4, 2)
        item.translate({1: 3})
        self.assertEqual(item.item, 4)

    def test___appearances__(self):
        answer = __appearances__('Bur Par Bur', ['Par', 'Bur', 'Mar'])
        self.assertEqual(len(answer), 3)
        postns = ['Par at 4', 'Bur at 0', 'Bur at 8']
        self.assertEqual([str(a) for a in answer], postns)
        self.assertEqual([a.item for a in answer], ['Par', 'Bur', 'Bur'])

    def test__first_appearances__(self):
        answer = __first_appearances__('Bur Par Bur', ['Par', 'Bur', 'Mar'])
        self.assertEqual(len(answer), 2)
        postns = ['Par at 4', 'Bur at 0']
        self.assertEqual([str(a) for a in answer], postns)
        self.assertEqual([a.item for a in answer], ['Par', 'Bur'])

    def test_ItemList__str__(self):
        i_l = ItemList('Burgundy Paris Burgundy',
                       self.game.variant.map.provinces)
        self.assertEqual(str(i_l), 'Burgundy at 0\nParis at 9\nBurgundy at 15')

    def test_ItemList__len__(self):
        i_l = ItemList('Burgundy Paris Burgundy',
                       self.game.variant.map.provinces)
        self.assertEqual(len(i_l), 3)

    def test_ItemList_loc(self):
        i_l = ItemList('Burgundy Paris Burgundy',
                       self.game.variant.map.provinces)   
        self.assertEqual(i_l.loc(1).name, 'Paris')
        i_l = ItemList('Burgundy',
                       self.game.variant.map.provinces)
        self.assertEqual(i_l.loc(1, require=False), None)
        with self.assertRaises(OrderInputError):
            i_l.loc(1)

    def test_ItemList_pos(self):
        i_l = ItemList('Burgundy Paris Burgundy',
                       self.game.variant.map.provinces)   
        self.assertEqual(i_l.pos(1), 9)
        i_l = ItemList('Burgundy',
                       self.game.variant.map.provinces)
        self.assertEqual(i_l.pos(1, require=False), None)
        with self.assertRaises(OrderInputError):
            i_l.loc(1)

    def test_ItelList_pos__negative_entry_(self):
        i_l = ItemList('A Paris move to Burgundy',
                       self.game.variant.map.provinces)  
        self.assertEqual(i_l.pos(-1), 16)

    def test_ItemList_first(self):
        i_l = ItemList('Bur Par Bur', ['Par', 'Bur', 'Mar'])   
        self.assertEqual(i_l.first(3), 'Par')
        self.assertEqual(i_l.first(6), 'Bur')
        self.assertEqual(i_l.first(after=1, before=2), None)
        i_l = ItemList('  ', ['Par', 'Bur', 'Mar'])
        self.assertEqual(i_l.first(after=1, before=5), None)

    def test_ItemList_getitme_(self):
        i_l = ItemList('Burgundy Paris Burgundy',
                       self.game.variant.map.provinces)   
        self.assertEqual(i_l[0].name, 'Burgundy')
        self.assertEqual(i_l[1].name, 'Paris')

if __name__ == '__main__':
    unittest.main()
