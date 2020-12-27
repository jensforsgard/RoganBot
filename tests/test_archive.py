#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Unittests for the archive module.
"""

import unittest
import adjudicator.game as gm


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

    def test_PositionArchive_centers(self):
        centers = self.game.position_archive.centers(self.game)
        for key in centers:
            self.assertEqual(centers[key], self.game.supply_centers[key])

if __name__ == '__main__':
    unittest.main()
        