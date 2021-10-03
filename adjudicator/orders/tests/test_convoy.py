""" Unittests for :cls:adjudicator.orders.Convoy

The tests should be run from the base directory.

"""


import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders import Convoy


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.unit = Mock()
        self.unit.owner.genitive = 'Austrian'
        self.unit.location.province = 'Denmark'
        self.unit.force = 'Army'

        self.object_order = Mock()
        self.object_order.__str__ = MagicMock(return_value='CC')
        self.object_order.target = 'Target'
        
        self.convoy = Convoy(self.unit, self.object_order)

    def tearDown(self):
        pass

    def test___init___1(self):
        self.assertEqual(
            self.unit,
            self.convoy.unit
        )

    def test___init___2(self):
        self.assertEqual(
            self.object_order,
            self.convoy.object_order
        )

    def test___init___3(self):
        self.assertEqual(
            self.convoy.max_status,
            'valid'
        )

    def test___init___4(self):
        self.assertEqual(
            self.convoy.min_status,
            'illegal'
        )

    def test___init___5(self):
        self.assertEqual(
            self.convoy.max_hold,
            34
        )

    def test___init___6(self):
        self.assertEqual(
            self.convoy.min_hold,
            1
        )

    def test___str___1(self):
        self.assertEqual(
            self.convoy.__str__(),
            'Austrian Army in Denmark convoys CC [unresolved].'
        )

    def test___legalize___1(self):
        orders = Mock()
        orders.order_of = MagicMock(return_value=None)
        
        self.convoy.__legalize__(orders)
        
        self.assertEqual(
            self.convoy.max_status,
            'illegal'
        )

    def test___legalize___2(self):
        orders = Mock()
        orders.order_of = MagicMock(return_value=self.unit)
        
        self.convoy.__legalize__(orders)
        
        self.assertEqual(
            self.convoy.max_status,
            'illegal'
        )

    def test___legalize___3(self):
        orders = Mock()
        orders.order_of = MagicMock(return_value=self.unit)
        
        self.unit.name = 'move'
        self.unit.target = 'Target'

        self.convoy.__legalize__(orders)
        
        self.assertEqual(
            self.convoy.min_status,
            'broken'
        )

    def test_resolve_dislodged_1(self):
        orders = Mock()
        orders.all_moves_to = MagicMock(return_value=[None])
        
        self.assertIsNone(
            self.convoy.resolve_dislodged(orders)
        )

    def test_resolve_dislodged_2(self):
        orders = Mock()
        orders.all_moves_to = MagicMock(return_value=[False])
        
        self.assertTrue(
            self.convoy.resolve_dislodged(orders)
        )

    def test_resolve_dislodged_3(self):
        orders = Mock()
        orders.all_moves_to = MagicMock(return_value=[1])
        
        self.assertFalse(
            self.convoy.resolve_dislodged(orders)
        )


if __name__ == '__main__':
    unittest.main()
