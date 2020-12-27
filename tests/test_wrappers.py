#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Unittests for the wrapper module.
"""

import unittest
import adjudicator.game as gm
from auxiliary.wrappers import require


class TestAdjudicator(unittest.TestCase) :

    @classmethod
    def setUpClass(cls):
        cls.game = gm.Game('Classic')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.game.reset()
        self.game.start()

    def tearDown(self):
        pass

    def test_require(self):
        @require
        def f(x, require=False):
            return x
        self.assertIsNone(f(None))
        self.assertIsNone(f(None, require=False))
        self.assertEqual(f(1), 1)
        with self.assertRaises(ValueError):
            f(None, require=True)
        
        

if __name__ == '__main__':
    unittest.main()
        