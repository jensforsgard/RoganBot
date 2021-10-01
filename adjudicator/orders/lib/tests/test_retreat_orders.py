""" Unittests for :cls:adjudicator.orders.lib.RetreatOrders

The tests should be run from the base directory.

"""

import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders.lib import RetreatOrders


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.mock = Mock()
        self.mock.target = Mock()
        self.mock.target.province = None
        
        self.orders = MagicMock()
        self.orders.__iter__.return_value = [self.mock]

    def tearDown(self):
        pass

    def test___init__1(self):
        self.mock.moves = MagicMock(return_value=False)

        self.collection = RetreatOrders(None, [self.mock])
        self.assertEqual(
            self.collection.orders,
            []
        )

    def test___init__2(self):
        self.mock.moves = MagicMock(return_value=True)
        self.orders.order_in = MagicMock(return_value=None)

        self.collection = RetreatOrders(None, self.orders)
        self.assertEqual(
            self.collection.orders,
            []
        )

    def test___init__3(self):
        self.mock.moves = MagicMock(return_value=True)
        self.orders.order_in = MagicMock(return_value=self.mock)

        self.collection = RetreatOrders(None, self.orders)
        self.assertEqual(
            self.collection.orders,
            []
        )

    def test___init__4(self):
        self.mock.moves = MagicMock(return_value=True)
        self.mock.convoy = True

        mock2 = Mock()
        mock2.moves = MagicMock(return_value=False)
        mock2.unit = 'Unit'

        self.orders.order_in = MagicMock(return_value=mock2)
        self.orders.blocks = MagicMock(return_value=[1, 2, 3])

        self.collection = RetreatOrders(lambda x, y, z: (y, z), self.orders)
        self.assertEqual(
            self.collection.orders,
            [('Unit', [1,2,3])]
        )


if __name__ == '__main__':
    unittest.main()
