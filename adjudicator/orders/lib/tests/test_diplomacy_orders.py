""" Unittests for :cls:adjudicator.orders.lib.DiplomacyOrders

The tests should be run from the base directory.

"""

import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders.lib import DiplomacyOrders


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.obj1 = Mock()
        cls.obj1.relevance = 3
        cls.obj1.sort_string = MagicMock(return_value=1)

        cls.obj2 = Mock()
        cls.obj2.relevance = 2
        cls.obj2.sort_string = MagicMock(return_value=3)

        cls.obj3 = Mock()
        cls.obj3.relevance = 1
        cls.obj3.sort_string = MagicMock(return_value=2)

        cls.objs = [cls.obj1, cls.obj2, cls.obj3]
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.orders = DiplomacyOrders(lambda x: x, self.objs)

    def tearDown(self):
        pass

    def test___init__(self):
        self.assertEqual(
            self.orders.orders,
            self.objs
        )

    def test_sort_by_sort_string(self):
        self.orders.sort()

        self.assertEqual(
            self.orders.orders,
            [self.obj1, self.obj3, self.obj2]
        )

    def test_sort_by_relevance(self):
        self.orders.sort('relevance')

        self.assertEqual(
            self.orders.orders,
            [self.obj3, self.obj2, self.obj1]
        )


if __name__ == '__main__':
    unittest.main()
