""" Unittests for the Variant class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Power, Variant, Map

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.variant = Variant('Classic')
        self.variant.load()
    
    def tearDown(self):
        pass

    def test__init__(self):
        variant = Variant('Classic')
        self.assertEqual(
            variant.name,
            'Classic'
        )

    def test__str__(self):
        self.assertEqual(
            self.variant.__str__(),
            'Classic'
        )

    def test_load(self):
        self.assertIsInstance(
            self.variant.name,
            str
        )
        self.assertIsInstance(
            self.variant.powers,
            tuple
        )
        self.assertIsInstance(
            self.variant.map,
            Map
        )
        self.assertIsInstance(
            self.variant.starting_year,
            int
        )
        self.assertIsInstance(
            self.variant.starting_positions,
            list
        )
        self.assertIsInstance(
            self.variant.win_condition,
            int
        )
        self.assertIsInstance(
            self.variant.unit_colors,
            dict
        )
        self.assertIsInstance(
            self.variant.province_colors,
            dict
        )
        self.assertIsInstance(
            self.variant.marker_size,
            int
        )
    
    def test_instance(self):
        germany = self.variant.instance('Germany', Power)
        self.assertIsInstance(
            germany,
            Power
        )
        self.assertEqual(
            germany.name,
            'Germany'
        )

if __name__ == '__main__':
    unittest.main()
