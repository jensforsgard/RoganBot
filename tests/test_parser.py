#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Unittests for the parser module.

"""

import unittest
import adjudicator.game as gm
import lib.parser as ps
from lib.errors import OrderInputError


class TestAdjudicator(unittest.TestCase) :

    @classmethod
    def setUpClass(cls):
        cls.game = gm.Game('Classic')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.game.reset()
        self.game.start()

    def tearDown(self):
        pass

    def test___deabbreviate__(self):
        parser = ps.Parser('Bre', self.game)
        self.assertEqual(parser.string, 'brest')
        parser = ps.Parser('-', self.game)
        self.assertEqual(parser.string, 'move')
        parser = ps.Parser('A', self.game)
        self.assertEqual(parser.string, 'army')

    def test_Decorator_load_orders(self):
        with self.assertRaises(OrderInputError):
            parser = ps.Parser('- S Convoy', self.game)
            parser.new()
            self.assertIsNotNone(parser.orders)

    def test_parse_Diplomacy_Hold(self):
        parser = ps.Parser('A Par H', self.game)
        order = parser.new()
        self.assertEqual(str(order), 'French Army in Paris holds [unresolved].')
        with self.assertRaises(OrderInputError):
            parser = ps.Parser('A Bur H', self.game)
            parser.new()
    
    def test_parse_Diplomacy_Move(self):
        parser = ps.Parser('A Par - Bur', self.game)
        order = parser.new()
        self.assertEqual(str(order), 'French Army in Paris move to Burgundy [unresolved].')

    def test_parse_Diplomacy_Move_convoyed(self):
        parser = ps.Parser('A Con - Gre via C', self.game)
        order = parser.new()
        self.assertEqual(str(order), ('Turkish Army in Constantinople move via convoy to '
                                      'Greece [unresolved].'))

    def test_parse_Diplomacy_Move_fleet_convoyed(self):
        with self.assertRaises(OrderInputError):
            parser = ps.Parser('F Ank - Sev via C', self.game)
            order = parser.new()

    def test_parse_Diplomacy_SupportHold(self):
        parser = ps.Parser('A Par S F Bre H', self.game)
        order = parser.new()
        self.assertEqual(str(order), 'French Army in Paris supports the Fleet in Brest holds [unresolved].')

    def test_parse_Diplomacy_SupportMove(self):
        parser = ps.Parser('A Vie S A Bud - Tri', self.game)
        order = parser.new()
        self.assertEqual(str(order), 'Austrian Army in Vienna supports the move Budapest '
                                     'to Trieste [unresolved].')

    def test_parse_Diplomacy_Convoy(self):
        with self.assertRaises(OrderInputError):
            parser = ps.Parser('F Bre C A Par - Pic', self.game)
            order = parser.new()
        self.game.order(['F Bre - ENG', 'A Par - Bre'])
        self.game.adjudicate()
        parser = ps.Parser('F ENG C A Bre - Wal', self.game)
        order = parser.new()
        self.assertEqual(str(order), 'French Fleet in English Channel convoys Brest '
                                     'to Wales [unresolved].')

    def test_parse_Retreat(self):
        self.game.order(['A War - Gal', 'A Mun - Bur'])
        self.game.adjudicate()
        self.game.order(['A Par - Bur', 'A Mar S move Bur from Par', 'A Bud - Gal',
                         'A Vie S A Bud - Gal'])
        self.game.adjudicate()
        parser = ps.Parser('A Bur - Bel', self.game)
        parser.new()
        self.assertEqual(str(self.game.orders.orders[0]), 'The Army in Burgundy retreats to Belgium.')
        parser = ps.Parser('A Gal disbands', self.game)
        parser.new()
        self.assertEqual(str(self.game.orders.orders[1]), 'The Army in Galicia disbands.')

    def test_parse_Builds(self):
        self.game.delete_unit('Paris')
        self.game.adjudicate()
        self.game.adjudicate()
        parser = ps.Parser('France Build 1 A Par', self.game)
        parser.new()
        self.assertEqual(str(self.game.orders.orders[0]), 'French build no. 1 is Army in Paris.')
        
    def test_old(self):
        parser = ps.Parser('A Par - Bur', self.game)
        self.assertEqual(str(parser.old()), 'French Army in Paris holds [unresolved].')


if __name__ == '__main__':
    unittest.main()
        