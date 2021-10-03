""" Unittests for :cls:adjudicator.orders.Support

The tests should be run from the base directory.

"""


import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders import Support


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
        self.unit.location = Mock()
        self.unit.location.__str__ = MagicMock(return_value='Denmark')
        self.unit.location.connections = [0]
        self.unit.force = 'Army'

        self.object_order = Mock()
        self.object_order.__str__ = MagicMock(return_value='CC')
        self.object_order.target = 'Target'
        
        self.support = Support(self.unit, self.object_order)

    def tearDown(self):
        pass

    def test___init___1(self):
        self.assertEqual(
            self.unit,
            self.support.unit
        )

    def test___init___2(self):
        self.assertEqual(
            self.object_order,
            self.support.object_order
        )

    def test___init___3(self):
        self.assertEqual(
            self.support.max_status,
            'valid'
        )

    def test___init___4(self):
        self.assertEqual(
            self.support.min_status,
            'illegal'
        )

    def test___init___5(self):
        self.assertEqual(
            self.support.max_hold,
            34
        )

    def test___init___6(self):
        self.assertEqual(
            self.support.min_hold,
            1
        )

    def test___str___(self):
        self.assertEqual(
            self.support.__str__(),
            'Austrian Army in Denmark supports CC [unresolved].'
        )

    def test___supports_move_on___1(self):
        self.object_order.target = Mock()
        self.assertFalse(
            self.support.__supports_move_on__('A')
        )

    def test___supports_move_on___2(self):
        self.object_order.target = Mock()
        self.object_order.target.province = 'A'
        self.assertTrue(
            self.support.__supports_move_on__('A')
        )

    def test___legalize__(self):
        orders = Mock()
        orders.order_of = MagicMock(return_value=None)

        location = Mock()
        location.province = 'B'

        game_map = Mock()
        game_map.locations = [location]

        self.object_order.name = 'C'

        self.support.__legalize__(orders, game_map)
        
        self.assertEqual(
            self.support.max_status,
            'illegal'
        )

    def test___resolve_attacked___1(self):
        orders = Mock()
        orders.all_moves_to = MagicMock(return_value=[True])
        
        self.support.__resolve_attacked__(orders)
        
        self.assertEqual(
            self.support.max_status,
            'cut'
        )

    def test___resolve_attacked___2(self):
        orders = Mock()
        orders.all_moves_to = MagicMock(return_value=[False])
        
        self.support.__resolve_attacked__(orders)
        
        self.assertEqual(
            self.support.min_status,
            'valid'
        )

    
if __name__ == '__main__':
    unittest.main()
