""" Unittests for :cls:adjudicator.orders.lib.BuildOrders

The tests should be run from the base directory.

"""


import unittest

from adjudicator.orders.lib import BuildOrders


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orders = BuildOrders(
        	lambda x, y: (x, y),
        	lambda x, y: (x, -y),
        	scs={1: [0], 2: [0, 0, 0, 0], 3: [0, 0, 0]},
        	hcs={1: 1, 2: 1, 3: 2},
        	units={1: 2, 2: 2, 3: 2}
        )
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test___init__(self):
        self.assertEqual(
            self.orders.orders,
            [(1, -1), (1, 2), (1, 3)]
        )

if __name__ == '__main__':
    unittest.main()
