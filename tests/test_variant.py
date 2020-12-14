#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Imports
# =============================================================================

import adjudicator.board as bd
import adjudicator.game as gm
#import adjudicator.orders as od
import adjudicator.variant as vr
import unittest
#import io
#import sys


# =============================================================================
# Tests
# =============================================================================

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

    def test_move_to(self):
        army = self.game.variant.map.instance('Army', bd.Force)
        burgundy = self.game.variant.map.locate(army, 'Burgundy')
        unit = self.game.unit_in('Constantinople')
        unit.move_to(burgundy)
        unit = self.game.unit_in('Burgundy')
        self.assertEqual(unit.owner.name, 'Turkey')
        self.assertEqual(unit.force.name, 'Army')
    
    def test_instance(self):
        germany = self.game.variant.instance('Germany', vr.Power)
        self.assertEqual(type(germany), vr.Power)
        self.assertEqual(germany.name, 'Germany')    
    
if __name__ == '__main__':
    unittest.main()
        