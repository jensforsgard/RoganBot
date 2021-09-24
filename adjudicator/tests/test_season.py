""" Unittests for the Season class.

The tests should be run from the base directory.

"""

import unittest

from unittest.mock import MagicMock

from adjudicator import Season

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.season = Season(1901)
    
    def tearDown(self):
        pass

    def test__init__(self):
        self.assertEqual(
            self.season.year,
            1900
        )
        self.assertEqual(
            self.season.name,
            'Spring'
        )
        self.assertEqual(
            self.season.phase,
            'Pregame'
        )
        self.assertEqual(
            self.season.count,
            0
        )

    def test__str__(self):
        self.assertEqual(
            self.season.__str__(),
            'Pregame in Spring 1900.'
        )

    def test_reset(self):
        # Progress one turn
        self.season.progress()
        
        # Reset
        mock = MagicMock()
        mock.starting_year = 100
        self.season.reset(mock)
        
        self.assertEqual(
            self.season.year,
            99
        )
        self.assertEqual(
            self.season.name,
            'Spring'
        )
        self.assertEqual(
            self.season.phase,
            'Pregame'
        )
        self.assertEqual(
            self.season.count,
            0
        )

    def test___set_name_phase__(self):
        self.season.__set_name_phase__()

        self.assertEqual(
            self.season.name,
            'Fall'
        )
        self.assertEqual(
            self.season.phase,
            'Builds'
        )

    def test___year_diff__(self):
        # Make sure the current count is as expected.
        self.assertEqual(
            self.season.count,
            0
        )

        self.assertEqual(
            self.season.__year_diff__(1),
            1
        )
        self.assertEqual(
            self.season.__year_diff__(5),
            1
        )
        self.assertEqual(
            self.season.__year_diff__(-1),
            0
        )
        self.assertEqual(
            self.season.__year_diff__(-5),
            -1
        )

    def test_progress(self):
        self.season.progress()

        self.assertEqual(
            self.season.phase,
            'Diplomacy'
        )

        self.season.progress(2)

        self.assertEqual(
            self.season.phase,
            'Diplomacy'
        )
        self.assertEqual(
            self.season.name,
            'Fall'
        )

        self.season.progress(3)

        self.assertEqual(
            self.season.phase,
            'Diplomacy'
        )
        self.assertEqual(
            self.season.year,
            1902
        )

    def test_rollback(self):    
        self.season.progress(7)
        self.season.rollback()

        self.assertEqual(
            self.season.year,
            1902
        )

        self.season.rollback(1)

        self.assertEqual(
            self.season.phase,
            'Builds'
        )
        self.assertEqual(
            self.season.name,
            'Fall'
        )

    def test_conclude(self):
        self.season.conclude()

        self.assertEqual(
            self.season.year,
            1900
        )
        self.assertEqual(
            self.season.phase,
            'Postgame'
        )
        
        with self.assertRaises(AssertionError):
            self.season.progress()

if __name__ == '__main__':
    unittest.main()
