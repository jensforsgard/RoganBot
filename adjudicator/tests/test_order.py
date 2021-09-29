""" Unittests for the Order class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Order
from adjudicator._orders import Support

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.order = Order()
        cls.support = Support('unit', 'object')

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_min_status(self):
        self.assertEqual(
            self.support.min_status,
            'illegal'
        )
        
        self.support.min_status = 'valid'
        self.assertEqual(
            self.support.min_status,
            'valid'
        )

    def test_max_status(self):
        self.assertEqual(
            self.support.max_status,
            'valid'
        )
        
        self.support.max_status = 'illegal'
        self.assertEqual(
            self.support.max_status,
            'illegal'
        )

    def test_reset(self):
        self.support.min_status = 'valid'
        self.support.max_status = 'illegal'
        self.support.reset()
        
        self.assertEqual(
            self.support.min_status,
            'illegal'
        )

if __name__ == '__main__':
    unittest.main()
