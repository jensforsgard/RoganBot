""" Unittests for the Geography class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Force
from adjudicator.board import Map

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map = Map('Classic')
        cls.map.load()
        cls.inland = cls.map.geographies[0]

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass


    def test__str__(self):
        self.assertEqual(
            self.inland.__str__(),
            'Inland'
        )

    def test__repr__(self):
        self.assertEqual(
            self.inland.__repr__(),
            ("Geography(name=Inland, map=Classic, force=Army, "
             "orders=['Move', 'Support', 'Hold'])")
        )

if __name__ == '__main__':
    unittest.main()
