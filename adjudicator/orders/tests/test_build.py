""" Unittests for :cls:adjudicator.Build

The tests should be run from the base directory.

"""

import unittest

from unittest.mock import Mock, MagicMock

from adjudicator.orders import Build


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.power = Mock()
        cls.power.genitive = 'Austrian'
        cls.power.name = 'Austria'
        cls.power.__str__ = MagicMock(return_value='Austria')
        
        cls.force = Mock()
        cls.force.name = 'Army'
        
        cls.location = Mock()
        cls.location.name = 'Adriatic Sea'
        cls.location.province = Mock()
        cls.location.province.name = 'Adriatic Sea'
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):


        self.build = Build(
            id=1,
            owner=self.power,
            force=self.force,
            location=self.location
        )

    def tearDown(self):
        pass

    def test___init__1(self):
        self.assertEqual(
            self.build.id,
            1
        )

    def test___init__2(self):
        self.assertEqual(
            self.build.owner.name,
            'Austria'
        )
        
    def test___init__3(self):
        self.assertEqual(
            self.build.force.name,
            'Army'
        )

    def test___init__4(self):
        self.assertEqual(
            self.build.location.name,
            'Adriatic Sea'
        )

    def test___str__(self):
        self.assertEqual(
            self.build.__str__(),
            'Austrian build no. 1 is Army in Adriatic Sea.'
        )

    def test_sort_string(self):
        self.assertEqual(
            self.build.sort_string(),
            'Austria1'
        )

    def test_province(self):
        self.assertEqual(
            self.build.province.name,
            'Adriatic Sea'
        )

    def test_postpone(self):
        self.build.postpone()

        self.assertIsNone(
            self.build.force
        )

    def test_postpone(self):
        self.build.postpone()

        self.assertIsNone(
            self.build.location
        )

    def test_postpone(self):
        self.build.postpone()

        self.assertIsNone(
            self.build.province
        )

    def test_invalid_action(self):
        self.build.invalid_action()

        self.assertIsNone(
            self.build.location
        )


if __name__ == '__main__':
    unittest.main()
