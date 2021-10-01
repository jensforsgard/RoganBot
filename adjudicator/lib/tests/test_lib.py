""" Unittests for :mod:`adjudicator.lib`

"""

import unittest

from unittest.mock import Mock

from adjudicator.lib import flatten


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


if __name__ == '__main__':
    unittest.main()
        