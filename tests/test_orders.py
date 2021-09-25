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
    od.Hold.resolve()
    od.Support.__supports_move_on__()
    od.Support.__legalize__()
    od.Support.__resolve_attacked__()
    od.Support.__resolve_left_alone__()
    od.Support.resolve()
    od.Convoy.__legalize__()
    od.Convoy.__resolve_dislodged__()
    od.Convoy.resolve()
    od.Disband.invalid_action()
    
"""

import adjudicator.orders as od
import adjudicator.game as gm
import unittest

from adjudicator import Build, Force

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
                          if isinstance(order, od.Move)), None)
    def tearDown(self):
        pass

    def test_orders_of_type(self):
        moves = od.orders_of_type(self.game.orders, od.Move)
        self.assertEqual(len(moves), 2)
        holds = od.orders_of_type(self.game.orders, od.Hold)
        self.assertEqual(len(holds), 19)
        convoys = od.orders_of_type(self.game.orders, od.Convoy)
        self.assertEqual(len(convoys), 1)
        supports = od.orders_of_type(self.game.orders, od.Support)
        self.assertEqual(len(supports), 1)

    # =========================================================================
    # Tests for the Diplomacy_Order class.
    # =========================================================================

    def test_reset(self):
        self.game.__resolve_diplomacy__()
        self.assertEqual(self.move.min_status, 'valid')
        self.assertTrue(self.move.resolved)
        self.move.reset()
        self.assertEqual(self.move.max_status, 'valid')
        self.assertEqual(self.move.min_status, 'illegal')
        self.assertEqual(self.move.max_hold, 1)
        self.assertEqual(self.move.min_hold, 1)
        self.assertFalse(self.move.resolved)
        
    def test_set_(self):
        self.assertIsNone(self.move.cutting)
        self.move.set_('cutting', True)
        self.assertTrue(self.move.cutting)
        self.move.set_('cutting', False)
        self.assertTrue(self.move.cutting)
    
    def test_moves(self):
        self.game.__resolve_diplomacy__()
        moves = [order.__str__() for order in self.game.orders 
                 if order.moves()]
        self.assertEqual(moves, ['French Army in Marseilles move via convoy to'
                                 ' Tuscany (succeeds).'])

    def test___decrease_status_to__(self):
        order = self.game.order_of(self.game.unit_in('Trieste'))
        order.__decrease_status_to__('illegal')
        self.assertEqual(order.max_status, 'illegal')

    def test___increase_status_to__(self):
        order = self.game.order_of(self.game.unit_in('Trieste'))
        order.__increase_status_to__('valid')
        self.assertEqual(order.max_status, 'valid')

    def test___status_at_least__(self):
        order = self.game.order_of(self.game.unit_in('Trieste'))
        self.assertFalse(order.__status_at_least__('valid'))
        order.__increase_status_to__('valid')
        self.assertTrue(order.__status_at_least__('valid'))

    def test___status_at_most__(self):
        order = self.game.order_of(self.game.unit_in('Trieste'))
        self.assertFalse(order.__status_at_most__('illegal'))
        order.__decrease_status_to__('illegal')
        self.assertTrue(order.__status_at_least__('illegal'))

    def test___is_resolved__(self):
        order = self.game.order_of(self.game.unit_in('Trieste'))
        self.assertFalse(order.__is_resolved__('hold'))
        order.resolve(self.game.variant, self.game.orders)
        self.assertTrue(order.__is_resolved__('hold'))

    def test___object_equivalent__(self):
        order = self.game.order_of(self.game.unit_in('Budapest'))
        hold = od.Hold(order.unit)
        move = od.Move(order.unit, False, order.object_order.target)
        self.assertTrue(order.__object_equivalent__(hold))
        self.assertFalse(order.__object_equivalent__(move))

    def test___object_of__(self):
        order = self.game.order_of(self.game.unit_in('Marseilles'))
        convoy = order.__object_of__(self.game.orders, od.Convoy)
        self.assertEqual(len(convoy), 1)
        self.assertEqual(type(convoy[0]), od.Convoy)

    def test___compute_hold_strengths__(self):
        order = self.game.order_of(self.game.unit_in('Marseilles'))
        order.__compute_hold_strengths__(self.game.orders)
        self.assertEqual(order.max_hold, 1)
        order = self.game.order_of(self.game.unit_in('Trieste'))
        order.__compute_hold_strengths__(self.game.orders)
        self.assertEqual(order.max_hold, 1)
        self.game.order('F Nap S A Rom H')
        order = self.game.order_of(self.game.unit_in('Rome'))
        order.__compute_hold_strengths__(self.game.orders)
        self.assertEqual(order.max_hold, 2)

    def test_blocks(self):
        self.game.__resolve_diplomacy__()
        order = self.game.order_of(self.game.unit_in('Constantinople'))
        self.assertEqual(order.blocks()[0].name, 'Constantinople')
        self.game.__resolve_diplomacy__()
        order = self.game.order_of(self.game.unit_in('Munich'))
        self.assertEqual(order.blocks()[0].name, 'Munich')

    def test_set_illegal(self):
        self.move.set_illegal()
        self.assertEqual(self.move.max_status, 'illegal')
        self.assertFalse(self.move.cutting)
        self.assertFalse(self.move.dislodging)
        self.assertTrue(self.move.failed)
        self.assertTrue(self.move.resolved)
        self.assertEqual(max(self.move.max_move.values()), 0)
        self.assertEqual(max(self.move.min_move.values()), 0)
    
    def test_set_resolved(self):
        self.move.set_resolved()
        self.assertFalse(self.move.resolved)
        self.move.resolve(self.game.variant, self.game.orders)
        self.assertTrue(self.move.resolved)

    # =========================================================================
    # Tests for the Move class.
    # =========================================================================

    def test___compute_move_strengths__(self):
        self.game.order('F Kie S Mun - Ber')
        self.move.__compute_move_strengths__(self.game.powers,
                                             self.game.orders)
        self.assertEqual(list(self.move.max_move.values()), [2,2,2,2,1,2,2,2])

    def test___convoy__(self):
        order = self.game.order_of(self.game.unit_in('Marseilles'))
        self.assertFalse(order.__convoy__(self.game.variant.map,
                                         self.game.orders, 'min_status'))
        self.assertTrue(order.__convoy__(self.game.variant.map,
                                         self.game.orders, 'max_status'))

    def test___repels__(self):
        order = self.game.order_of(self.game.unit_in('Munich'))
        move = self.game.order_of(self.game.unit_in('Berlin'))
        self.assertFalse(order.__repels__(move))
        self.game.order('A Ber - Sil')
        self.game.__resolve_diplomacy__()
        order = self.game.order_of(self.game.unit_in('Munich'))
        move = self.game.order_of(self.game.unit_in('Berlin'))
        self.assertTrue(order.__repels__(move))
        self.game.order('A Ber - Sil')

    def test___test_opposed_by__(self):
        berlin = self.game.unit_in('Berlin')
        order = self.game.order_of(berlin)
        self.assertFalse(self.move.__opposed_by__(order))
        self.game.order('A Ber - Mun')
        order = self.game.order_of(berlin)
        self.assertTrue(self.move.__opposed_by__(order))

    def test___supports_attack_on_self__(self):
        self.game.order('F Smy S A Ank - Con')
        self.game.order('A Ank - Con')
        self.game.order('A Con - Smy')
        order1 = self.game.order_of(self.game.unit_in('Smyrna'))
        order2 = self.game.order_of(self.game.unit_in('Ankara'))
        order3 = self.game.order_of(self.game.unit_in('Constantinople'))
        self.assertTrue(order3.__supports_attack_on_self__(order1))
        self.assertFalse(order3.__supports_attack_on_self__(order2))

    def test__move_sort_string__(self):
        self.game.order('A Ank - Con')
        strings = [order.sort_string() for order in self.game.orders]
        self.assertIn('Turkey20', strings)


    # =========================================================================
    # The Hold Class
    # =========================================================================

    def test__hold_sort_string__(self):
        strings = [order.sort_string() for order in self.game.orders]
        self.assertIn('Turkey20', strings)


    # =========================================================================
    # The Support Class
    # =========================================================================

    def test__support_sort_string__(self):
        self.game.order('A Ank S F Smy - Con')
        strings = [order.sort_string() for order in self.game.orders]
        self.assertIn('Turkey20', strings)


    # =========================================================================
    # The Convoy Class
    # =========================================================================

    def test__convoy_sort_string__(self):
        self.game.order(['F Bre - ENG', 'A Par - Pic'])
        self.game.adjudicate()
        self.game.order('F ENG C A Pic - Wal')
        strings = [order.sort_string() for order in self.game.orders]
        self.assertIn('France7', strings)


    # =========================================================================
    # The Retreat Class
    # =========================================================================

    def test_resolve(self):
        self.game.delete_unit('Venice')
        self.game.delete_unit('Naples')
        self.game.add_unit('Fleet', 'Austria', 'Tyrrhenian Sea')
        self.game.add_unit('Army', 'Austria', 'Venice')
        self.game.add_unit('Army', 'France', 'Apulia')
        self.game.add_unit('Fleet', 'France', 'Western Mediterranean')
        self.game.add_unit('Fleet', 'France', 'Tunis')
        self.game.order(['A Ven - Apu', 'A Rom S A Ven - Apu'])
        self.game.order(['F WMS - TYS', 'F Tun S F WMS - TYS'])
        self.game.adjudicate()
        self.game.order(['F TYS - Nap', 'A Apu - Nap'])
        self.game.adjudicate()
        self.assertEqual(len(self.game.units), 24)

    def test__retreat_sort_string__(self):
        retreat = od.Retreat(25, self.game.units[0], [])
        self.assertEqual(retreat.sort_string(), 'Austria1')


    # =========================================================================
    # The Disband Class
    # =========================================================================

    def test__disband_sort_string__(self):
        disband = od.Disband(25, self.game.powers[0])
        self.assertEqual(disband.sort_string(), 'Austria25')

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


    # =========================================================================
    # Test the Retreat class
    # =========================================================================

if __name__ == '__main__':
    unittest.main()
