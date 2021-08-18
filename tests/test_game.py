#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Unittests for the game module.

Methods which are currently not tested:
    game.show()
    game.__sort_units__()
    
Methods which are not tested here, but tested by test_adjudicator_DATC
    game.__resolve_diplomacy__()
    game.__resolve_orders__()
    game.__resolve_paradoxes__()
    game.__resolve_circular_movement__()
    game.__execute_diplomacy__()
    game.__setup_diplomacy__()
    game.__setup_retreats__()
    game.__setup_builds__()
    game.adjudicate()

"""

import unittest
import io
import sys
from geopandas import GeoDataFrame
import adjudicator.board as bd
import adjudicator.game as gm
import adjudicator.orders as od
import adjudicator.variant as vr
from lib.itemlist import ItemList
from lib.archive import (OrderArchive, PositionArchive)


class TestAdjudicator(unittest.TestCase) :

    @classmethod
    def setUpClass(cls):
        cls.gameFvA = gm.Game('ClassicFvA')
        cls.gameRPS = gm.Game('RPS')
        cls.game = gm.Game('Classic')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.game.reset()
        self.game.start()
        self.gameFvA.reset()
        self.gameFvA.start()
        self.gameRPS.reset()
        self.gameRPS.start()

    def tearDown(self):
        pass

    
    def test_info(self):
        capturedOutput = io.StringIO()
        out = sys.stdout
        sys.stdout = capturedOutput
        self.gameRPS.display('variant')
        self.gameRPS.display('map')
        self.gameRPS.display('provinces')
        self.gameRPS.display('supply centers')
        self.gameRPS.display('abbreviations')
        sys.stdout = out
        string = ("RPS\nRPS\n['Conakry', 'Monrovia', 'Freetown']\n['Conakry', "
                  "'Monrovia', 'Freetown']\n"
                  "- move\nS support\nC convoy\nH hold\nB build\n"
                  "D disband\nR retreat\nA army\nF fleet\nSt Saint\n"
                  "destroy disband\nCon Conakry\nMon Monrovia\nFre Fre"
                  "etown\n")
        self.assertEqual(capturedOutput.getvalue(), string)

    def test_current_position(self):
        answer = self.gameRPS.current_position()
        unit = {'force': 'Army', 'location': 0, 'power': 'Guinea'}
        self.assertEqual(answer['units'][0], unit)

    def test___archive_position__(self):
        self.game.__archive_position__()
        self.assertEqual(self.game.position_archive.last(), 
                          self.game.current_position())

    def test___archive_orders__(self):
        self.gameRPS.__archive_orders__()
        orders = ['Guinean Army in Conakry holds [unresolved].',
                  'Liberian Army in Monrovia holds [unresolved].']
        self.assertEqual(self.gameRPS.order_archive.last(), orders)

    def test___unit_color__(self):
        answer = self.gameRPS.__unit_color__(self.gameRPS.powers[0])
        self.assertEqual(answer, 'royalblue')

    def test_start(self):
        game = gm.Game('RPS')
        game.start()
        self.assertEqual(game.season.__str__(), 'Diplomacy in Spring 1990.')
        units = [unit.__str__() for unit in game.units]
        self.assertEqual(units,['Guinean Army in Conakry.',
                                'Liberian Army in Monrovia.'])
        orders = [order.__str__() for order in game.orders]
        answer = ['Guinean Army in Conakry holds [unresolved].',
                  'Liberian Army in Monrovia holds [unresolved].']
        self.assertEqual(orders, answer)
        supplies = [supp.name for supp in game.supply_centers[game.powers[0]]]
        self.assertEqual(supplies,['Conakry'])
        home = [supp.name for supp in game.supply_centers[game.powers[0]]]
        self.assertEqual(home, ['Conakry'])
        self.assertEqual(game.position_archive.loc(0)['phase'], 'Diplomacy')

    def test_start_error(self):
        with self.assertRaises(AssertionError):
            self.game.start()

    def test_reset(self):
        self.game.adjudicate()
        self.game.reset()
        self.assertEqual(self.game.season.name,'Spring')
        self.assertEqual(self.game.season.phase,'Pregame')
        self.assertEqual(self.game.season.year,1901)
        self.assertEqual(self.game.units, [])
        self.assertEqual(self.game.supply_centers, {})
        self.assertEqual(self.game.home_centers, {})
        self.assertEqual(self.game.orders, [])
        self.assertIs(self.game.winner, None)
        self.assertIsInstance(self.game.position_archive, PositionArchive)
        self.assertIsInstance(self.game.order_archive, OrderArchive)
        self.assertEqual(len(self.game.position_archive), 0)
        self.assertEqual(len(self.game.order_archive), 0)

    def test_rollback(self):
        self.gameRPS.order('A Mon - Fre')
        self.gameRPS.adjudicate()
        self.gameRPS.rollback()
        self.gameRPS.rollback()
        units = [unit.__str__() for unit in self.gameRPS.units]
        orders = [order.__str__() for order in self.gameRPS.orders]
        self.assertIn('Liberian Army in Monrovia.', units)
        order = 'Liberian Army in Monrovia move to Freetown [unresolved].'
        self.assertIn(order, orders)
        self.assertEqual(self.gameRPS.season.name, 'Spring')

    def test_rollback_winner(self):
        self.game.adjudicate()
        self.game.winner = self.game.powers[0]
        self.game.rollback()
        self.assertIsNone(self.game.winner)

    def test_load_graphics(self):
        self.assertIsNone(self.game.graphics)
        self.game.__load_graphics__()
        self.assertIsInstance(self.game.graphics, GeoDataFrame)
        names = list(self.game.graphics.name)
        for location in self.game.variant.map.locations:
            self.assertIn(location.name, names)

    def test___sort_orders_by_relevance__(self):
        self.gameFvA.add_unit('Fleet', 'France', 'Gulf of Lyon')
        self.gameFvA.order(['GoL C Mar - Tus', 'A Mar - Tus',
                            'A Tri S Vie H'])
        self.gameFvA.__sort_orders__(by='relevance')
        orders = [order.__str__() for order in self.gameFvA.orders]
        answer = ['French Fleet in Gulf of Lyon convoys Marseilles to Tuscany '
                  '[unresolved].', 'French Army in Marseilles move to Tuscany '
                  '[unresolved].', 'Austrian Fleet in Trieste supports the Arm'
                  'y in Vienna holds [unresolved].', 'Austrian Army in Budapes'
                  't holds [unresolved].']
        self.assertEqual(orders[:4], answer)

    def test_unit_in(self):
        province = next((prov for prov in self.game.provinces
                          if prov.name == 'Berlin'), None)
        unit = self.game.unit_in(province)
        self.assertEqual(unit.owner.name, 'Germany')
        self.assertEqual(unit.force.name, 'Army')

    def test_unit_in_require(self):
        province = next((prov for prov in self.game.provinces
                          if prov.name == 'Finland'), None)
        self.assertEqual(self.game.unit_in(province), None)
        self.assertEqual(self.game.unit_in(province, require=False), None)
        with self.assertRaises(ValueError):
            self.game.unit_in(province, require=True)

    def test_order_of(self):
        self.game.order('A Budapest move to Vienna.')
        unit = self.game.units[0]
        self.assertEqual(unit.location.name, 'Budapest')
        order = self.game.order_of(unit)
        self.assertEqual(type(order), od.Move)
        self.assertEqual(order.target.name, 'Vienna')
        
    def test_order_in(self):
        self.game.order('A Budapest move to Vienna.')
        province = next((prov for prov in self.game.provinces
                          if prov.name == 'Budapest'), None)
        order = self.game.order_in(province)
        self.assertEqual(type(order), od.Move)
        self.assertEqual(order.target.name, 'Vienna')

    def test_order_in_require(self):
        province = next((prov for prov in self.game.provinces
                          if prov.name == 'Finland'), None)
        self.assertEqual(self.game.order_in(province), None)
        self.assertEqual(self.game.order_in(province, require=False), None)
        with self.assertRaises(ValueError):
            self.game.order_in(province, require=True)
        
    def test_adjustment_order(self):
        self.game.order(['A Ber - Sil', 'A War - Pru'])
        self.game.adjudicate()
        self.game.order(['A Sil - War'])
        self.game.adjudicate()
        power = next((p for p in self.game.powers if p.name == 'Germany'))
        order = self.game.adjustment_order(1, power)
        self.assertEqual(type(order), od.Build)
        power = next((p for p in self.game.powers if p.name == 'Russia'))
        order = self.game.adjustment_order(1, power)
        self.assertEqual(type(order), od.Disband)

    def test_units_of(self):
        power = next((p for p in self.game.powers if p.name == 'Germany'))
        units = [p.province.name for p in self.game.units_of(power)]
        self.assertIn('Berlin', units)
        self.assertIn('Kiel', units)
        self.assertIn('Munich', units)

    def test_occupied_provinces(self):
        power = next((p for p in self.game.powers if p.name == 'Germany'))
        provs = [p.name for p in self.game.occupied_provinces(power)]
        self.assertIn('Berlin', provs)
        self.assertIn('Kiel', provs)
        self.assertIn('Munich', provs)

    def test_orders_of(self):
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Munich')
        self.game.adjudicate()
        self.game.adjudicate()
        power = next((p for p in self.game.powers if p.name == 'Germany'))
        orders = [o.id for o in self.game.build_orders_of(power)
                  if o.owner.name == 'Germany']
        self.assertIn(1, orders)
        self.assertIn(2, orders)

    def test_open_home_centers(self):
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Munich')
        self.game.order('A War - Sil')
        self.game.adjudicate()
        self.game.order('A Sil - Ber')
        self.game.adjudicate()
        power = next((p for p in self.game.powers if p.name == 'Germany'))
        centers = [c.name for c in self.game.open_home_centers(power)]
        self.assertIn('Munich', centers)     
        self.assertEqual(1, len(centers))    

    def test_instance(self):
        entity = self.game.instance('Bulgaria', bd.Province)
        self.assertEqual(type(entity), bd.Province)
        self.assertEqual(entity.name, 'Bulgaria')
        entity = self.game.instance('Germany', vr.Power)
        self.assertEqual(type(entity), vr.Power)
        self.assertEqual(entity.name, 'Germany')
        entity = self.game.instance('Fleet', bd.Force)
        self.assertEqual(type(entity), bd.Force)
        self.assertEqual(entity.name, 'Fleet')
        entity = self.game.instance('Inland', bd.Geography)
        self.assertEqual(type(entity), bd.Geography)
        self.assertEqual(entity.name, 'Inland')

    def test_locate(self):
        force = self.game.instance('Fleet', bd.Force)
        location = self.game.locate(force, 'Spain (south coast)')
        self.assertEqual(type(location), bd.Location)
        self.assertEqual(location.name, 'Spain (south coast)')
        self.assertEqual(location.force.name, 'Fleet')
        self.assertEqual(location.geography.name, 'Coast')

    def test___unresolved_count__(self):
        count = self.game.__unresolved_count__()
        self.assertEqual(count, 22)
        self.game.__resolve_diplomacy__()
        count = self.game.__unresolved_count__()
        self.assertEqual(count, 0)       

    def test___next_unit_id__(self):
        number = self.game.__next_unit_id__()
        exist = [unit.id for unit in self.game.units]
        self.assertEqual(number, max(exist)+1)

    def test_add_unit(self):
        self.game.add_unit('Army', 'Germany', 'Armenia')
        unit = self.game.unit_in('Armenia')
        self.assertEqual(unit.owner.name, 'Germany')
        self.assertEqual(unit.force.name, 'Army')   
        province = self.game.instance('Armenia', bd.Province)
        unit = self.game.unit_in(province)
        self.assertEqual(unit.owner.name, 'Germany')
        self.assertEqual(unit.force.name, 'Army')   

    def test_delete_unit(self):
        self.game.delete_unit('Berlin')
        province = self.game.instance('Munich', bd.Province)
        self.game.delete_unit(province)
        unit = self.game.unit_in('Kiel')
        self.game.delete_unit(unit)
        self.assertEqual(len(self.game.units), 19)

    def test___adjust_supply_centers__(self):
        munich = self.game.instance('Munich', bd.Province)
        russia = self.game.instance('Russia', vr.Power)
        germany = self.game.instance('Germany', vr.Power)
        self.game.delete_unit(munich)
        self.game.add_unit('Army', russia, 'Munich')
        self.game.__adjust_supply_centers__()
        self.assertIn(munich, self.game.supply_centers[russia])
        self.assertNotIn(munich, self.game.supply_centers[germany])
    
    def test_order(self):
        self.game.add_unit('Fleet', 'Germany', 'Gulf of Lyon')
        self.game.order(['A Berlin move to Kiel.', 'A Mar S Par - Bur', 
                          'F GoL C Mar - Tus'])
        order = [order.__str__() for order in self.game.orders]
        self.assertIn('German Army in Berlin move to Kiel [unresolved].',
                      order)
        self.assertIn('German Fleet in Gulf of Lyon convoys Marseilles to Tusc'
                      'any [unresolved].', order)
        self.assertIn('French Army in Marseilles supports the move Paris '
                      'to Burgundy [unresolved].', order)

    def test___resolve_builds__(self):
        self.game.delete_unit('Berlin')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.order('Germany B 1 A Ber')
        self.assertFalse(self.game.orders[0].resolved)
        self.game.__resolve_builds__()
        self.assertTrue(self.game.orders[0].resolved)
        order = self.game.orders[0].__str__()
        self.assertEqual(order, 'German build no. 1 is Army in Berlin.')

    def test__resolve_retreats__(self):
        self.game.order('A Mun - Bur')
        self.game.order('A War - Sil')        
        self.game.order('A Vie - Boh')  
        self.game.order('A Bud - Gal')  
        self.game.adjudicate()
        self.game.order('A Par - Bur')
        self.game.order('A Mar S A Par - Bur')
        self.game.order('A Gal - Sil')
        self.game.order('A Boh S A Gal - Sil')
        self.game.adjudicate()
        self.game.order('A Bur - Mun')
        self.game.order('A Sil - Mun')
        self.game.__resolve_retreats__()
        orders = [order.__str__() for order in self.game.orders]
        self.assertIn('The Army in Burgundy retreats to Munich (fails).', orders)
        self.assertIn('The Army in Silesia retreats to Munich (fails).', orders)

    def test___execute_builds__(self):
        self.game.delete_unit('Berlin')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.order('Germany B 1 A Ber')
        self.game.__resolve_builds__()
        self.game.__execute_builds__()
        self.assertEqual(len(self.game.units), 22)
    
    def test__execute_retreats__(self):
        self.game.order('A Mun - Bur')
        self.game.order('A War - Sil')        
        self.game.order('A Vie - Boh')  
        self.game.order('A Bud - Gal')  
        self.game.adjudicate()
        self.game.order('A Par - Bur')
        self.game.order('A Mar S A Par - Bur')
        self.game.order('A Gal - Sil')
        self.game.order('A Boh S A Gal - Sil')
        self.game.adjudicate()
        self.game.order('A Bur - Mun')
        self.game.order('A Sil - Mun')
        self.game.__resolve_retreats__()
        self.game.__execute_retreats__()
        self.assertEqual(len(self.game.units), 20)
    
    def test_conclude(self):
        self.game.conclude(True)
        self.assertIsNone(self.game.winner)
        russia = self.game.instance('Russia', vr.Power)
        self.game.supply_centers[russia] = range(18)
        self.game.conclude(True)
        self.assertEqual(self.game.winner, russia)      

    def test___sort_orders__(self):
        self.game.order(['A Bud - Gal', 'F Lon - NTH', 'A Lvp - Yor',
                         'A Par - Bur', 'A Mar S Par - Bur', 'A Mun - Bur',
                         'A Ven - Tyr'])
        self.game.adjudicate()
        self.game.order(['A Yor - Nwy via C', 'F NTH C Yor - Nwy', 
                         'A Tyr - Mun', 'A Bur S A Tyr - Mun'])
        self.game.adjudicate()
        self.game.order('A Mun - Boh')
        self.game.adjudicate()
        info = self.game.info('orders')
        expected = ('English build no. 1 is postponed.\nGerman disband no. 1 '
                    'is by default.\nItalian build no. 1 is postponed.')
        self.assertEqual(info, expected)
        self.game.__sort_orders__()
        self.assertEqual(info, expected)

if __name__ == '__main__':
    unittest.main()
        