""" Unittests for :cls:`adjudicator.orders.OrderCollection`

The tests should be run from the base directory.

"""

import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders import OrderCollection


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.element1 = Mock()
        cls.element1.province = 'A'
        cls.element1.unit = 'a'
        cls.element1.sort_string = MagicMock(return_value=6)
        cls.element1.blocks = MagicMock(return_value=[1,2])

        cls.element2 = Mock()
        cls.element2.province = 'B'
        cls.element2.unit = 'b'
        cls.element2.sort_string = MagicMock(return_value=5)
        cls.element2.blocks = MagicMock(return_value=[3])

        cls.element3 = Mock()
        cls.element3.province = 'C'
        cls.element3.unit = 'c'
        cls.element3.sort_string = MagicMock(return_value=4)
        cls.element3.blocks = MagicMock(return_value=[1, 4])

        cls.elements = [cls.element1, cls.element2, cls.element3]

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.collection = OrderCollection([
            self.element1,
            self.element2,
            self.element3
        ])

    def tearDown(self):
        pass

    def test___init__(self):
        self.assertEqual(
            self.collection.orders,
            self.elements
        )

    def test___iter__(self):
        
        for k in self.collection:
            self.assertIn(
                k,
                self.elements
            )

    def test___len__(self):
        self.assertEqual(
            len(self.collection),
            3
        )

    def test_insert_1(self):
        self.collection.insert('D')
        
        self.assertEqual(
            self.collection.orders[-1],
            'D'
        )

    def test_insert_2(self):
        self.collection.insert('D')

        self.assertEqual(
            len(self.collection.orders),
            4
        )

    def test_remove(self):
        self.collection.remove(self.element2)

        self.assertEqual(
            self.collection.orders,
            [self.element1, self.element3]
        )

    def test_remove_unit(self):
        self.collection.remove_unit('b')
        
        self.assertNotIn(
            self.element2,
            self.collection.orders
        )

    def test_order_in_1(self):
        order = self.collection.order_in('C')
        
        self.assertEqual(
            order,
            self.element3
        )

    def test_order_in_2(self):
        order = self.collection.order_in('D')
        
        self.assertIsNone(order)

    def test_order_in_3(self):
        with self.assertRaises(ValueError):
            self.collection.order_in('D', require=True)

    def test_order_of(self):
        order = self.collection.order_of('a')
        
        self.assertEqual(
            order,
            self.element1
        )

    def test_blocks_1(self):
        self.assertEqual(
            set(self.collection.blocks()),
            {1, 2, 3, 4}
        )

    def test_blocks_2(self):
        self.assertEqual(
            len(self.collection.blocks()),
            4
        )

    def test_blocks_3(self):
        self.assertIsInstance(
            self.collection.blocks(),
            list
        )

    def test_sort(self):
        self.collection.sort()

        self.assertEqual(
        	self.collection.orders,
        	[self.element3, self.element2, self.element1]
        )

if __name__ == '__main__':
    unittest.main()
