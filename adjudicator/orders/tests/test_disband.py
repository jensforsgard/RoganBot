""" Unittests for :cls:adjudicator.orders.lib.Disband

The tests should be run from the base directory.

"""


import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders import Disband


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.owner = Mock()
        cls.owner.genitive = 'Austrian'
        cls.owner.__str__ = MagicMock(return_value='Austria')
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.unit = Mock()
        self.unit.owner = self.owner
        self.unit.force = 'Army'
        self.unit.location.province.name = 'Budapest'

        self.disband = Disband(
            id=1,
            owner=self.owner,
            unit=self.unit
        )

    def tearDown(self):
        pass

    def test___init___1(self):
        self.assertEqual(
            self.disband.id,
            1
        )

    def test___init___2(self):
        self.assertEqual(
            self.disband.owner,
            self.owner
        )

    def test___init___3(self):
        self.assertEqual(
            self.disband.unit,
            self.unit
        )

    def test___init___4(self):
        self.assertFalse(
            self.disband.resolved
        )

    def test___str__(self):
        self.assertEqual(
            self.disband.__str__(),
            'Austrian disband no. 1 is Army in Budapest.'
        )

    def test_province(self):
        self.assertEqual(
            self.disband.province.name,
            'Budapest'
        )

    def test_sort_string(self):
        self.assertEqual(
            self.disband.sort_string(),
            'Austria1'
        )

    def test_postpone(self):
        self.disband.postpone()

        self.assertIsNone(
            self.disband.unit
        )

    def test_unit_1(self):
        self.disband.unit = None
        self.assertIsNone(
            self.disband.unit
        )

    def test_unit_2(self):
        self.disband.unit = None
        self.disband.unit = self.unit

        self.assertEqual(
            self.disband.unit,
            self.unit
        )

    def test_invalid_action(self):
        self.disband.unit = None
        
        self.disband.invalid_action(
            [self.unit],
            []
        )

        self.assertEqual(
            self.disband.unit.owner,
            self.owner
        )


if __name__ == '__main__':
    unittest.main()
