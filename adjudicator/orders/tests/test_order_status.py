""" Unittests for :cls:adjudicator.orders.OrderStatus

The tests should be run from the base directory.

"""

import unittest

from adjudicator.orders import OrderStatus

class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.status = OrderStatus('illegal')

    def tearDown(self):
        pass

    def test___init__(self):
        self.assertEqual(
            self.status.status,
            'illegal'
        )
        
        with self.assertRaises(AssertionError):
            OrderStatus('nothing')

    def test___str___(self):
        self.assertEqual(
            self.status.__str__(),
            'illegal'
        )

    def test_set_accepted(self):
        self.status.set('cut')
        self.assertEqual(
            self.status.status,
            'cut'
        )

    def test_set_declined(self):
        with self.assertRaises(AssertionError):
            self.status.set('wrong')

    def test_value(self):
        self.assertEqual(
            self.status.value,
            self.status.statuses['illegal']
        )
    
    def test___lt__class(self):
        self.assertTrue(
            self.status < OrderStatus('valid')
        )

    def test___lt__string(self):
        self.assertTrue(
            self.status < 'valid'
        )

    def test___gt__class(self):
        self.assertFalse(
            self.status > OrderStatus('valid')
        )

    def test___gt__string(self):
        self.assertFalse(
            self.status > 'valid'
        )

    def test___eq__class_1(self):
        self.assertFalse(
            self.status == OrderStatus('valid')
        )

    def test___eq__class_2(self):
        self.assertTrue(
            self.status == OrderStatus('illegal')
        )

    def test___eq__string_1(self):
        self.assertFalse(
            self.status == 'valid'
        )

    def test___eq__string_2(self):
        self.assertTrue(
            self.status == 'illegal'
        )


if __name__ == '__main__':
    unittest.main()
