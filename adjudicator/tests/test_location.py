""" Unittests for the Location class.

The tests should be run from the base directory.

"""
    
import unittest

from adjudicator import Force, Geography, Location, Map, Province

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map = Map('Classic')
        cls.map.load()

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.province = self.map.provinces[34]
        self.location = self.map.locations[28]
        self.geography = self.location.geography
    
    def tearDown(self):
        pass

    def test___init__(self):
        location = Location(
            id=1,
            name='Spain (south coast)',
            connections=[2,3,4],
            geography='Coast',
            map=self.map
        )

        self.assertEqual(
            location.id,
            1
        )
        self.assertEqual(
            location.name,
            'Spain (south coast)'
        )
        self.assertEqual(
            location.connections,
            (2,3,4)
        )
        self.assertIsInstance(
            location.geography,
            Geography
        )
        self.assertEqual(
            location.geography.name,
            'Coast'
        )
        self.assertIsInstance(
            location.force,
            Force
        )
        self.assertEqual(
            location.force.name,
            'Fleet'
        )
        self.assertIsInstance(
            location.province,
            Province
        )
        self.assertEqual(
            location.province.name,
            'Spain'
        )

    def test___str__(self):
        self.assertEqual(
            self.location.name,
            'Constantinople'
        )

    def test_reaches_location(self):
        self.assertTrue(
            self.location.reaches_location(5)
        )
        self.assertTrue(
            self.location.reaches_location(
                self.map.locations[91]
            )
        )
        self.assertFalse(
            self.location.reaches_location(15)
        )

    def test_reaches_province(self):
        self.assertFalse(
            self.location.reaches_province(self.province)
        )

        province = self.map.locations[91].province
        self.assertTrue(
            self.location.reaches_province(province)
        )

    def test_named(self):
        location = self.map.locations[-23]
        self.assertTrue(
        	location.named('Saint Petersburg (south coast)')
        )
        self.assertTrue(
        	location.named('Saint Petersburg')
        )
        self.assertFalse(
        	location.named('Moscow')
        )

if __name__ == '__main__':
    unittest.main()
