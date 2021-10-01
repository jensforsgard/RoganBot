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

import adjudicator.game as gm

from geopandas import GeoDataFrame
from adjudicator import (
    Force, Geography, Location, Power, Province
)

from adjudicator.orders import (
    Build, Disband
)

from lib.itemlist import ItemList
from lib.archive import (OrderArchive, PositionArchive)
from lib.classes import dict_string


class TestAdjudicator(unittest.TestCase) :

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.gameFvA = gm.Game('ClassicFvA')
        self.gameFvA.start()

        self.gameRPS = gm.Game('RPS')
        self.gameRPS.start()

        self.game = gm.Game('Classic')
        self.game.start()

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
                  "destroy disband\n['Con', 'Mon', 'Fre']\n")
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
        self.assertEqual(self.game.season.year, 1900)
        self.assertEqual(self.game.units, [])
        self.assertEqual(self.game.supply_centers, {})
        self.assertEqual(self.game.home_centers, {})
        self.assertEqual(len(self.game.orders), 0)
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

    def test_adjustment_order(self):
        self.game.order(['A Ber - Sil', 'A War - Pru'])
        self.game.adjudicate()
        self.game.order(['A Sil - War'])
        self.game.adjudicate()
        power = next((p for p in self.game.powers if p.name == 'Germany'))
        order = self.game.adjustment_order(1, power)
        self.assertEqual(type(order), Build)
        power = next((p for p in self.game.powers if p.name == 'Russia'))
        order = self.game.adjustment_order(1, power)
        self.assertEqual(type(order), Disband)

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
        entity = self.game.instance('Bulgaria', Province)
        self.assertEqual(type(entity), Province)
        self.assertEqual(entity.name, 'Bulgaria')
        entity = self.game.instance('Germany', Power)
        self.assertEqual(type(entity), Power)
        self.assertEqual(entity.name, 'Germany')
        entity = self.game.instance('Fleet', Force)
        self.assertEqual(type(entity), Force)
        self.assertEqual(entity.name, 'Fleet')
        entity = self.game.instance('Inland', Geography)
        self.assertEqual(type(entity), Geography)
        self.assertEqual(entity.name, 'Inland')

    def test_locate(self):
        force = self.game.instance('Fleet', Force)
        location = self.game.locate(force, 'Spain (south coast)')
        self.assertEqual(type(location), Location)
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
        province = self.game.instance('Armenia', Province)
        unit = self.game.unit_in(province)
        self.assertEqual(unit.owner.name, 'Germany')
        self.assertEqual(unit.force.name, 'Army')   

    def test_delete_unit(self):
        self.game.delete_unit('Berlin')
        province = self.game.instance('Munich', Province)
        self.game.delete_unit(province)
        unit = self.game.unit_in('Kiel')
        self.game.delete_unit(unit)
        self.assertEqual(len(self.game.units), 19)

    def test___adjust_supply_centers__(self):
        munich = self.game.instance('Munich', Province)
        russia = self.game.instance('Russia', Power)
        germany = self.game.instance('Germany', Power)
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
        self.assertFalse(self.game.orders.orders[0].resolved)
        self.game.__resolve_builds__()
        self.assertTrue(self.game.orders.orders[0].resolved)
        order = self.game.orders.orders[0].__str__()
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
        russia = self.game.instance('Russia', Power)
        self.game.supply_centers[russia] = range(18)
        self.game.conclude(True)
        self.assertEqual(self.game.winner, russia)      

if __name__ == '__main__':
    unittest.main()
        