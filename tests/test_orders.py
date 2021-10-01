#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Unittests for the orders module.

Functions/Mehtods not tested here, all of which are methods tested through
the test_adjudicator_DATC module:    
    
    od.Move.__stronger_than__()
    od.Move.__weaker_than__()
    od.Move.__stronger_attack__()
    od.Move.__weaker_attack__()
    od.Move.__bounces__()
    od.Move.__attacks__()
    od.Move.__resolve_lagality__()
    od.Move.__resolve_hth__()
    od.Move.__resolve__()
    od.Move.__resolve_empty__()
    od.Move.__resolve_repels__()
    od.Move.__resolve_opposed__()
    od.Move.__resolve_support_on_self__()
    od.Move.__resolve_attack__()
    od.Support.__supports_move_on__()
    od.Support.__legalize__()
    od.Support.__resolve_attacked__()
    od.Support.__resolve_left_alone__()
    od.Support.resolve()
    od.Convoy.__legalize__()
    od.Convoy.__resolve_dislodged__()
    od.Convoy.resolve()
    
"""

import adjudicator.game as gm
import unittest

from adjudicator import Force

from adjudicator.orders import Build, Convoy, Hold, Move


class TestOrders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = gm.Game('Classic')
        cls.game.start()
        cls.army = cls.game.variant.map.instance('Army', Force)
        cls.fleet = cls.game.variant.map.instance('Fleet', Force)
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.game.reset()
        self.game.start()
        location = self.game.variant.map.locate(self.fleet, 'Gulf of Lyon')
        self.game.add_unit(self.army, self.game.powers[0], location)
        self.game.order(['A Mun - Ber', 'F GoL C A Mar - Tus', 
                         'A Mar - Tus via C', 'A Bud S A Vie - Gal'])
        self.move = next((order for order in self.game.orders 
                          if isinstance(order, Move)), None)
    def tearDown(self):
        pass

    # =========================================================================
    # Tests for the Move class.
    # =========================================================================

    def test___compute_move_strengths__(self):
        self.game.order('F Kie S Mun - Ber')
        self.move.__compute_move_strengths__(self.game.powers,
                                             self.game.orders)
        self.assertEqual(list(self.move.max_move.values()), [2,2,2,2,1,2,2,2])

    def test___convoy__(self):
        order = self.game.orders.order_of(self.game.unit_in('Marseilles'))
        self.assertFalse(order.__convoy__(self.game.variant.map,
                                         self.game.orders, 'min_status'))
        self.assertTrue(order.__convoy__(self.game.variant.map,
                                         self.game.orders, 'max_status'))

    def test___repels__(self):
        order = self.game.orders.order_of(self.game.unit_in('Munich'))
        move = self.game.orders.order_of(self.game.unit_in('Berlin'))
        self.assertFalse(order.__repels__(move))
        self.game.order('A Ber - Sil')
        self.game.__resolve_diplomacy__()
        order = self.game.orders.order_of(self.game.unit_in('Munich'))
        move = self.game.orders.order_of(self.game.unit_in('Berlin'))
        self.assertTrue(order.__repels__(move))
        self.game.order('A Ber - Sil')

    def test___test_opposed_by__(self):
        berlin = self.game.unit_in('Berlin')
        order = self.game.orders.order_of(berlin)
        self.assertFalse(self.move.__opposed_by__(order))
        self.game.order('A Ber - Mun')
        order = self.game.orders.order_of(berlin)
        self.assertTrue(self.move.__opposed_by__(order))

    def test___supports_attack_on_self__(self):
        self.game.order('F Smy S A Ank - Con')
        self.game.order('A Ank - Con')
        self.game.order('A Con - Smy')
        order1 = self.game.orders.order_of(self.game.unit_in('Smyrna'))
        order2 = self.game.orders.order_of(self.game.unit_in('Ankara'))
        order3 = self.game.orders.order_of(self.game.unit_in('Constantinople'))
        self.assertTrue(order3.__supports_attack_on_self__(order1))
        self.assertFalse(order3.__supports_attack_on_self__(order2))

    def test__move_sort_string__(self):
        self.game.order('A Ank - Con')
        strings = [order.sort_string for order in self.game.orders]
        self.assertIn('Turkey20', strings)

    # =========================================================================
    # The Support Class
    # =========================================================================

    def test__support_sort_string__(self):
        self.game.order('A Ank S F Smy - Con')
        strings = [order.sort_string for order in self.game.orders]
        self.assertIn('Turkey20', strings)

    # =========================================================================
    # Adjudicator scenarios tests
    # =========================================================================

    def test_bounced_when_opposed(self):
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Army', 'Austria', 'Tyrolia')
        self.game.add_unit('Army', 'Austria', 'Venice')
        self.game.add_unit('Army', 'France', 'Rome')
        self.game.add_unit('Army', 'France', 'Piedmont')
        self.game.order(['A Rom - Ven', 'A Pie S A Rom - Ven'])
        self.game.order(['A Ven - Rom', 'F Tri - Ven', 'A Tyr S F Tri - Ven'])
        self.game.adjudicate()
        self.assertEqual(self.game.season.name, 'Fall')
        self.assertEqual(self.game.season.phase, 'Diplomacy')

    def test_no_self_dislodgent_after_bounced(self):
        self.game.delete_unit('Saint Petersburg')
        self.game.add_unit('Army', 'Russia', 'Saint Petersburg')
        self.game.add_unit('Fleet', 'France', 'Norway')
        self.game.add_unit('Fleet', 'France', 'Sweden')
        self.game.order(['A Nwy S A Mos - StP', 'A Swe - Fin'])
        self.game.order(['A StP - Fin', 'A Mos - StP'])
        self.game.adjudicate()
        self.assertEqual(self.game.season.name, 'Fall')
        self.assertEqual(self.game.season.phase, 'Diplomacy')

if __name__ == '__main__':
    unittest.main()
