""" Unittests for the Province class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Province

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.province = Province(
            14,
            name='Burgundy',
            short='Bur',
            supply_center=False
        )

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass


    def test__str__(self):
        self.assertEqual(
            self.province.__str__(),
            'Burgundy'
        )

    def test__repr__(self):
        self.assertEqual(
            self.province.__repr__(),
            ('Province(idn=14, name=Burgundy, short=Bur, '
             'supply_center=False)')
        )

if __name__ == '__main__':
    unittest.main()
