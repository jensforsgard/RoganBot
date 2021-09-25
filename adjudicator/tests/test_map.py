""" Unittests for the Map class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Force, Geography, Location, Map, Province

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.RPSmap = Map('RPS')
        cls.RPSmap.load()
        cls.ClassicMap = Map('Classic')
        cls.ClassicMap.load()
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test___init__(self):
        instance = Map('Classic')
        self.assertEqual(
            instance.name,
            'Classic',
        )
        self.assertFalse(
            instance.loaded
        )

    def test___str__(self):
        self.assertEqual(
            self.RPSmap.__str__(),
            'RPS'
        )

    def test_info(self):
        self.assertEqual(
            self.RPSmap.info('abbreviations')[0],
            'Con'
        )
        self.assertEqual(
            self.RPSmap.info('provinces')[0],
            'Conakry'
        )
        self.assertEqual(
            self.RPSmap.info('locations')[0],
            'Conakry'
        )

    def test_load(self):
        # instance self.map has been loaded.
        self.assertEqual(
            self.RPSmap.orders,
            ('Hold', 'Move', 'Support')
        )
        self.assertEqual(
            list(map(str, list(self.RPSmap.forces))),
            ['Army']
        )
        self.assertEqual(
            list(map(str, list(self.RPSmap.geographies))),
            ['Inland']
        )
        self.assertEqual(
            str(self.RPSmap.provinces[0]),
            'Conakry'
        )
        self.assertEqual(
            str(self.RPSmap.locations[0]),
            'Conakry'
        )
        self.assertEqual(
            self.RPSmap.force_abbreviations,
            {}
        )
        self.assertEqual(
            self.RPSmap.abbreviations['Con'],
            'Conakry'
        )
        self.assertEqual(
            len(self.RPSmap.supply_centers),
            3
        )
        self.assertEqual(
            len(self.RPSmap.provinces),
            3
        )
        self.assertEqual(
            len(self.RPSmap.locations),
            3
        )

    def test_instance(self):
        answer = self.ClassicMap.instance(
            'Inland',
            Geography
        )
        self.assertIsInstance(
            answer,
            Geography
        )
        self.assertEqual(
            str(answer),
            'Inland'
        )

        answer = self.ClassicMap.instance(
            'Denmark',
            Province
        )
        self.assertIsInstance(
            answer,
            Province
        )
        self.assertEqual(
            str(answer),
            'Denmark'
        )

        answer = self.ClassicMap.instance(
            'Army',
            Force
        )
        self.assertIsInstance(
            answer,
            Force
        )
        self.assertEqual(
            str(answer),
            'Army'
        )

    def test_instances(self):
        answer = self.ClassicMap.instances(
            ['Denmark', 'Burgundy'],
            Province
        )
        self.assertEqual(
            len(answer),
            2
        )
        self.assertEqual(
            answer[0].name,
            'Denmark'
        )
        self.assertEqual(
            answer[1].name,
            'Burgundy'
        )
        self.assertIsInstance(
            answer[0],
            Province
        )

    def test_locations_of(self):
        province = self.ClassicMap.instance(
            'Spain',
            Province
        )
        answer = list(map(
            str,
            self.ClassicMap.locations_of(province))
        )

        self.assertIn(
            'Spain',
            answer
        )
        self.assertIn(
            'Spain (south coast)',
            answer
        )
        self.assertIn(
            'Spain (north coast)',
            answer
        )

    def test_locate(self):
        force = self.ClassicMap.instance(
            'Fleet',
            Force
        )
        answer = self.ClassicMap.locate(
            force,
            'Norway'
        )

        self.assertIsInstance(
            answer,
            Location
        )
        self.assertEqual(
            str(answer),
            'Norway'
        )
        
        # Test with the origin keyword set
        origin = self.ClassicMap.locate(
            force,
            'Gascony'
        )
        answer = self.ClassicMap.locate(
            force,
            'Spain',
            origin=origin
        )
        self.assertIsInstance(
            answer,
            Location
        )
        self.assertEqual(
            str(answer),
            'Spain (north coast)'
        )

    def test_one_adjacent(self):
        force = self.ClassicMap.instance(
            'Fleet',
            Force
        )
        province = self.ClassicMap.instance(
            'Brest',
            Province
        )
        location1 = self.ClassicMap.locate(
            force,
            'English Channel'
        )
        location2 = self.ClassicMap.locate(
            force,
            'Smyrna'
        )
        self.assertTrue(
            self.ClassicMap.one_adjacent(
                [location1, location2],
                province
            )
        )
        self.assertFalse(
            self.ClassicMap.one_adjacent(
                [location2],
                province
            )
        )

    def test_has_path(self):
        source = self.ClassicMap.instance(
            'Brest',
            Province
        )
        target = self.ClassicMap.instance(
            'Wales',
            Province
        )
        force = self.ClassicMap.instance(
            'Fleet',
            Force
        )
        locs = self.ClassicMap.locate(
            force,
            'English Channel'
        )

        self.assertTrue(
            self.ClassicMap.has_path(source, target, [locs])
        )
 
        self.assertFalse(
            self.ClassicMap.has_path(source, target, [])
        )

if __name__ == '__main__':
    unittest.main()
