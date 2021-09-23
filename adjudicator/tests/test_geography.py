""" Unittests for the Geography class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Geography
from adjudicator.board import Map

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map = Map('Classic')
        cls.map.load()

        cls.geography = Geography(
            name='Inland',
            map_=cls.map,
            force='Army',
            orders=['Hold']
        )

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test__init__(self):
        self.assertEqual(
            self.geography.name,
            'Inland'
        )
        self.assertEqual(
            self.geography.force.name,
            'Army'
        )
        self.assertEqual(
            self.geography.orders,
            ['Hold']
        )

    def test__str__(self):
        self.assertEqual(
            self.geography.__str__(),
            'Inland'
        )

if __name__ == '__main__':
    unittest.main()
