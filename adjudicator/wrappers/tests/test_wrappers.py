""" Unittests for :mod:`adjudicator.wrappers`

"""

import unittest

from adjudicator.wrappers import require


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

    def test_require(self):
        @require
        def f(x, require=False):
            return x

        self.assertIsNone(
            f(None)
        )
        
        self.assertIsNone(
            f(None, require=False)
        )
        
        self.assertEqual(
            f(1),
            1
        )

        with self.assertRaises(ValueError):
            f(None, require=True)        


if __name__ == '__main__':
    unittest.main()
        