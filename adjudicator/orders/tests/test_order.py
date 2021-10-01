""" Unittests for :cls:adjudicator.orders.Order

The tests should be run from the base directory.

"""

import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders import Order, OrderStatus


class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.order = Order()
        self.order._min_status = OrderStatus('illegal')
        self.order._max_status = OrderStatus('valid')

        self.order.province = 1

    def tearDown(self):
        pass

    def test_min_status_getter(self):
        self.assertEqual(
            self.order.min_status,
            'illegal'
        )
        
    def test_min_status_setter(self):
        self.order.min_status = 'valid'
        self.assertEqual(
            self.order.min_status,
            'valid'
        )

    def test_max_status_getter(self):
        self.assertEqual(
            self.order.max_status,
            'valid'
        )

    def test_max_status_setter(self):
        self.order.max_status.set('illegal')
        self.assertEqual(
            self.order.max_status.status,
            'illegal'
        )

    def test_reset(self):
        self.order.min_status = 'valid'
        self.order.max_status = 'illegal'
        self.order.reset()
        
        self.assertEqual(
            self.order.min_status.status,
            'illegal'
        )

    def test_set_(self):
        self.order.attr = 'A'
        self.order.set_('attr', 'B')
        
        self.assertEqual(
            self.order.attr,
            'A'
        )

    def test___resolved___1(self):
        self.assertFalse(
            self.order.__resolved__('status')
        )

    def test___resolved___2(self):
        self.order.max_status = 'illegal'
        self.assertTrue(
            self.order.__resolved__('status')
        )

    def test__compute_hold_strengths__(self):
        orders = Mock()
        orders.aids = MagicMock(return_value=[self.order])
        
        self.order.max_hold = 3
        self.order.min_hold = 0
        
        self.order.__compute_hold_strengths__(orders)
        
        self.assertEqual(
            self.order.min_hold,
            1
        )

        self.assertEqual(
            self.order.max_hold,
            2
        )

    def test_moves(self):
        self.assertFalse(
            self.order.moves()
        )

    def test_blocks(self):
        self.assertEqual(
            self.order.blocks(),
            [1]
        )

    def test___object_equivalent___1(self):
        
        self.order.relevance = 3
        
        mock = Mock()
        mock.relevance = 1
        mock.province = 1
        
        self.assertTrue(
            self.order.__object_equivalent__(mock)
        )

    def test___object_equivalent___2(self):
        
        self.order.relevance = 2
        
        mock = Mock()
        mock.relevance = 1
        mock.province = 1
        
        self.assertFalse(
            self.order.__object_equivalent__(mock)
        )

    def test___object_equivalent___3(self):
        
        self.order.relevance = 1
        
        mock = Mock()
        mock.relevance = 2
        mock.province = 1
        
        self.assertFalse(
            self.order.__object_equivalent__(mock)
        )

    def test___object_equivalent___4(self):
        
        self.order.relevance = 1
        
        mock = Mock()
        mock.relevance = 3
        mock.province = 2
        
        self.assertFalse(
            self.order.__object_equivalent__(mock)
        )


if __name__ == '__main__':
    unittest.main()
