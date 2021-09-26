""" Unittests for the Retreat class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Disband, Retreat

from adjudicator.game import Game

class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.game = Game('Classic')
        self.game.start()

        self.retreat = Retreat(
            id=2,
            unit=self.game.units[0],
            forbidden=[]
        )

    def tearDown(self):
        pass

    def test___init__(self):
        self.assertEqual(
            self.retreat.id,
            2
        )
        self.assertEqual(
            self.retreat.unit,
            self.game.units[0]
        )
        self.assertEqual(
            self.retreat.forbidden,
            []
        )
        self.assertIsInstance(
            self.retreat.order,
            Disband
        )
        self.assertFalse(
            self.retreat.resolved
        )
        self.assertIsNone(
            self.retreat.legal
        )
        self.assertIsNone(
            self.retreat.disbands
        )

    def test___str__(self):
        self.assertEqual(
            self.retreat.__str__(),
            'The Army in Budapest disbands.'
        )

    def test_province(self):
        self.assertEqual(
            self.retreat.province.name,
            'Budapest'
        )

    def test_disbands(self):
        self.assertIsNone(
            self.retreat.disbands
        )

        self.retreat.disbands = True
        self.assertTrue(
            self.retreat._disbands
        )

    def test_legal(self):
        self.assertIsNone(
            self.retreat.legal
        )

        self.retreat.legal = False
        self.assertFalse(
            self.retreat._legal
        )

    def test_resolved(self):
        self.assertFalse(
            self.retreat.resolved
        )

        self.retreat.legal = False
        self.retreat.disbands = True
        self.assertTrue(
            self.retreat._resolved
        )

    def test_sort_string(self):
        self.assertEqual(
            self.retreat.sort_string(),
            'Austria1'
        )

    def test_reset(self):
        self.retreat.disbands = True
        self.retreat.legal = True
        self.retreat.reset()
        self.assertIsNone(
            self.retreat.disbands
        )
        self.assertIsNone(
            self.retreat.legal
        )
        self.assertFalse(
            self.retreat.resolved
        )

    def test_resolve(self):
        self.game.clear()
        self.game.add_units([
            ['Fleet', 'Austria', 'Tyrrhenian Sea'],
            ['Army', 'Austria', 'Venice'],
            ['Army', 'France', 'Apulia'],
            ['Fleet', 'France', 'Western Mediterranean'],
            ['Fleet', 'France', 'Tunis'],
            ['Army', 'Italy', 'Rome']
        ])
        self.game.order([
            'A Ven - Apu', 'A Rom S A Ven - Apu',
            'F WMS - TYS', 'F Tun S F WMS - TYS'
        ])
        self.game.adjudicate()
        self.game.order(['F TYS - Nap', 'A Apu - Nap'])
        self.game.adjudicate()
        self.assertEqual(
            len(self.game.units),
            4
        )

if __name__ == '__main__':
    unittest.main()
