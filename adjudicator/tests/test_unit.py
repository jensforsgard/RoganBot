""" Unittests for the Unit class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Unit, Variant

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.variant = Variant('Classic')
        cls.variant.load()

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.unit = Unit(
            id=1,
            owner=self.variant.powers[0],
            force=self.variant.map.forces[0],
            location=self.variant.map.locations[68]
        )
    
    def tearDown(self):
        pass

    def test__init__(self):
        self.assertEqual(
            self.unit.id,
            1
        )
        self.assertEqual(
            self.unit.owner.name,
            'Austria'
        )
        self.assertEqual(
            self.unit.force.name,
            'Army'
        )
        self.assertEqual(
            self.unit.location.name,
            'Norway'
        )

    def test__str__(self):
        self.assertEqual(
            self.unit.__str__(),
            'Austrian Army in Norway.'
        )

    def test_unit_type(self):
        self.assertEqual(
            self.unit.unit_type(),
            'Army'
        )

    def test_move_to(self):
        self.unit.move_to(
        	self.variant.map.locations[65]
        )

        self.assertEqual(
            self.unit.province.name,
            'North Africa'
        )

    def test_sort_string(self):
        self.assertEqual(
            self.unit.sort_string(),
            'Austria1'
        )

if __name__ == '__main__':
    unittest.main()
