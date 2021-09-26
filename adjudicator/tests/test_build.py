""" Unittests for the Build class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Build, Variant

class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.variant = Variant('Classic')
        cls.variant.load()
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.build = Build(
            id=1,
            owner=self.variant.powers[0],
            force=self.variant.map.forces[0],
            location=self.variant.map.locations[0]
        )

    def tearDown(self):
        pass

    def test___init__(self):
        self.assertEqual(
            self.build.id,
            1
        )
        self.assertEqual(
            self.build.owner.name,
            'Austria'
        )
        self.assertEqual(
            self.build.force.name,
            'Army'
        )
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

    def test_invalid_action(self):
        self.build.invalid_action()

        self.assertIsNone(
            self.build.location
        )

    def test_postpone(self):
        self.build.postpone()

        self.assertIsNone(
            self.build.force
        )
        self.assertIsNone(
            self.build.location
        )
        self.assertIsNone(
            self.build.province
        )

if __name__ == '__main__':
    unittest.main()
