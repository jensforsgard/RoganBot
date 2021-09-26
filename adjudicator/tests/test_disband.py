""" Unittests for the Disband class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Disband, Unit

from adjudicator.game import Game

class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = Game('Classic')
        cls.game.start()
        
        cls.owner = cls.game.powers[0]
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.disband = Disband(
            id=1,
            owner=self.owner,
            unit=self.game.units_of(self.owner)[0]
        )

    def tearDown(self):
        pass

    def test___init__(self):
        self.assertEqual(
            self.disband.id,
            1
        )
        self.assertEqual(
            self.disband.owner,
            self.owner
        )
        self.assertEqual(
            self.disband.unit.owner,
            self.owner
        )

    def test___str__(self):
        self.assertEqual(
            self.disband.__str__(),
            'Austrian disband no. 1 is Army in Budapest.'
        )

    def test_province(self):
        self.assertEqual(
            self.disband.province.name,
            'Budapest'
        )

    def test_unit(self):
        unit = self.disband.unit
        
        self.disband.unit = None
        self.assertIsNone(
            self.disband.unit
        )

        self.disband.unit = unit
        self.assertEqual(
            self.disband.unit,
            unit
        )

    def test_invalid_action(self):
        self.disband.unit = None
        
        self.disband.invalid_action(
            self.game.units_of(self.owner),
            []
        )

        self.assertIsInstance(
            self.disband.unit,
            Unit
        )
        self.assertEqual(
            self.disband.unit.owner,
            self.owner
        )

    def test_postpone(self):
        self.disband.postpone()

        self.assertIsNone(
            self.disband.unit
        )

if __name__ == '__main__':
    unittest.main()
