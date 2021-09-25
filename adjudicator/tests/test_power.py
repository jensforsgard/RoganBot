""" Unittests for the Power class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Power

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        cls.power = Power(
            name='Germany',
            genitive='German',
            home_centers=['Berlin', 'Munich', 'Kiel']
        )
    
    def tearDown(self):
        pass

    def test__init__(self):
        self.assertEqual(
            self.power.name,
            'Germany'
        )
        self.assertEqual(
            self.power.genitive,
            'German'
        )
        self.assertEqual(
            self.power.supply_centers,
            ['Berlin', 'Munich', 'Kiel']
        )

    def test__str__(self):
        self.assertEqual(
            self.power.__str__(),
            'Germany'
        )

if __name__ == '__main__':
    unittest.main()
