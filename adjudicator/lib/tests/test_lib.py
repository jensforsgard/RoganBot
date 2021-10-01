""" Unittests for :mod:`adjudicator.lib`

"""

import unittest

from unittest.mock import Mock

from adjudicator.lib import flatten, isorderinstance


class TestAdjudicator(unittest.TestCase) :

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_flatten(self):
        self.assertEqual(
            flatten([[1,2], [3,4]]),
            [1,2,3,4]
        )

    def test_isorderintsance_true(self):
        self.order = Mock()
        self.order.relevance = 2
        
        self.assertTrue(
            isorderinstance(self.order, 'move')
        )

    def test_isorderintsance_false(self):
        self.order = Mock()
        self.order.relevance = 1
        
        self.assertFalse(
            isorderinstance(self.order, 'move')
        )

if __name__ == '__main__':
    unittest.main()
        