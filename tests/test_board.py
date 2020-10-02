#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Functions/Mehtods not tested here:
    
    bd.Map.check_consistency()
        Method to check that the information stored in a .json file is ok.

"""
    


# =============================================================================
# Imports
# =============================================================================

import adjudicator.board as bd
import unittest


# =============================================================================
# Tests
# =============================================================================

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map = bd.Map('Classic')
        cls.map.load()
        cls.province = cls.map.provinces[34]
        cls.location = cls.map.locations[28]
        cls.geography = cls.location.geography

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self.season = bd.Season('Spring', 'Diplomacy', 1900)
    
    def tearDown(self):
        pass

    def test_flatten(self):
        answer = bd.flatten([[1], [2, 3], [[4]]])
        self.assertEqual(answer, [1,2,3,[4]])

    def test_despecify(self):
        geo = self.geography
        string = 'Fleet (south coast).'
        self.assertEqual(bd.despecify(string, geo), 'Fleet.')

    def test_first_named(self):
        first = bd.first_named(self.map.provinces, 'Burgundy')
        self.assertEqual(first.name, 'Burgundy')
        self.assertIsInstance(first, bd.Province)
        self.assertFalse(first.supply_center)

    def test_union(self):
        union = bd.union([{1:2}, {3:4}])
        self.assertEqual(union, {1:2, 3:4})

    def test_make_instances(self):
        dicnry = {1: {'name': '10', 'short': '11', 'supply center': '12'},
                  2: {'name': '20', 'short': '21', 'supply center': '22'}}
        answer = bd.make_instances(dicnry, bd.Province)
        self.assertEqual(type(answer[0]), bd.Province)
        self.assertEqual(type(answer[1]), bd.Province)
        self.assertEqual(answer[0].name,'10')
        self.assertEqual(answer[1].short_form,'21')
        self.assertEqual(answer[0].supply_center,'12')


    # =========================================================================
    # Tests for the Location class.
    # =========================================================================

    def test_reaches_location(self):
        self.assertTrue(self.location.reaches_location(5))
        self.assertTrue(self.location.reaches_location(self.map.locations[91]))
        self.assertFalse(self.location.reaches_location(15))
        with self.assertRaises(TypeError) :
            self.location.reaches_location('Finland')

    def test_reaches_province(self):
        province = self.map.locations[91].province
        self.assertTrue(self.location.reaches_province(self.map, province))

    def test_named(self):
        location = self.map.locations[-23]
        self.assertTrue(location.named('Saint Petersburg (south coast)'))
        self.assertTrue(location.named('Saint Petersburg'))


    # =========================================================================
    # Tests for the Map class.
    # =========================================================================

    def test_load(self):
        self.assertEqual(self.map.orders,
                         ['Hold', 'Move', 'Support', 'Convoy'])
        self.assertEqual([force.name for force in self.map.forces],
                          ['Army', 'Fleet'])
        self.assertEqual([geo.name for geo in self.map.geographies],
                         ['Inland', 'Coast', 'Sea'])
        self.assertEqual(self.map.provinces[0].name, 'Adriatic Sea')
        self.assertEqual(self.map.locations[89].name, 'Skagerrack')
        self.assertEqual(self.map.forces_dict,
                         {'(s)': '(south coast)', '(n)': '(north coast)'})
        self.assertEqual(self.map.province_dict['AEG'], 'Aegean Sea')
        self.assertEqual(self.map.supply_centers[8].name, 'Edinburgh')
        self.assertEqual(len(self.map.supply_centers), 34)
        self.assertEqual(len(self.map.provinces), 75)
        self.assertEqual(len(self.map.locations), 120)

    def test_forces(self):
        force = self.map.forces[1]
        self.assertIsInstance(force, bd.Force)
        self.assertEqual(force.name, 'Fleet')
        self.assertEqual(force.specifiers, ['(south coast)', '(north coast)'])
        self.assertIsInstance(force.short_forms, dict)
        self.assertEqual(force.short_forms['(s)'], '(south coast)')
    
    def test_orders(self):
        self.assertEqual(set(self.map.orders), 
                         {'Hold', 'Move', 'Support', 'Convoy'})

    def test_geographies(self):
        geos = self.map.geographies
        geo = geos[0]
        self.assertEqual(len(geos), 3)
        self.assertIsInstance(geo, bd.Geography)
        self.assertEqual(geo.name, 'Inland')

    def test_provinces(self):
        provs = self.map.provinces
        pro = provs[17]
        self.assertEqual(len(provs), 75)
        self.assertIsInstance(pro, bd.Province)
        self.assertEqual(pro.name, 'Constantinople')
        self.assertEqual(pro.short_form, 'Con')
        self.assertTrue(pro.supply_center)

    def test_locations(self):
        locs = self.map.locations
        loc = locs[47]
        self.assertEqual(len(locs), 120)
        self.assertIsInstance(loc, bd.Location)
        self.assertEqual(loc.name, 'Ionian Sea')
        self.assertIsInstance(loc.geography, bd.Geography)
        self.assertIsInstance(loc.province, bd.Province)
        self.assertIsInstance(loc.connections, list)
        self.assertEqual(loc.connections, [0, 1, 3, 7, 31, 41, 63, 105, 109])
        self.assertEqual(loc.province.name, 'Ionian Sea')
    
    def test_forces_dict(self):
        dictionary = self.map.forces_dict
        self.assertEqual(dictionary['(s)'], '(south coast)')

    def test_province_dict(self):
        dictionary = self.map.province_dict
        self.assertEqual(dictionary['ADR'], 'Adriatic Sea')
    
    def test_supplies(self):
        scs = self.map.supply_centers
        self.assertEqual(len(scs), 34)
        self.assertIsInstance(scs[0], bd.Province)

    def test_intance(self):
        answer = self.map.instance('Inland', bd.Geography)
        self.assertEqual(type(answer), bd.Geography)
        self.assertEqual(answer.name, 'Inland')
        answer = self.map.instance('Denmark', bd.Province)
        self.assertEqual(type(answer), bd.Province)
        self.assertEqual(answer.name, 'Denmark')
        answer = self.map.instance('Army', bd.Force)
        self.assertEqual(type(answer), bd.Force)
        self.assertEqual(answer.name, 'Army')

    def test_locations_of(self):
        province = self.map.instance('Spain', bd.Province)
        answer = [loc.name for loc in self.map.locations_of(province)]
        self.assertIn('Spain', answer)
        self.assertIn('Spain (south coast)', answer)
        self.assertIn('Spain (north coast)', answer)

    def test_locate(self):
        force = self.map.instance('Fleet', bd.Force)
        answer = self.map.locate(force, 'Norway')
        self.assertEqual(type(answer), bd.Location)
        self.assertEqual(answer.name, 'Norway')    
        source = self.map.locate(force, 'Gascony')
        answer = self.map.locate(force, 'Spain', source)
        self.assertEqual(type(answer), bd.Location)
        self.assertEqual(answer.name, 'Spain (north coast)')   

    def test_has_path(self):
        source = self.map.instance('Brest', bd.Province)
        target = self.map.instance('Wales', bd.Province)
        force = self.map.instance('Fleet', bd.Force)
        locs = self.map.locate(force, 'English Channel')
        answer = self.map.has_path(source, target, [locs])   
        self.assertTrue(answer)
        answer = self.map.has_path(source, target, [])   
        self.assertTrue(not answer)


    # =========================================================================
    # Tests for the Season class.
    # =========================================================================

    def test_progress(self):
        self.season.progress()
        self.assertEqual(self.season.phase, 'Retreats')
        self.season.progress()
        self.assertEqual(self.season.name, 'Fall')        
        self.season.progress()
        self.assertEqual(self.season.name, 'Fall')    
        self.season.progress()
        self.assertEqual(self.season.phase, 'Builds')   
        self.season.progress()
        self.assertEqual(self.season.year, 1901)    

    def test_regress(self):
        self.season.regress()
        self.assertEqual(self.season.year, 1899) 
        self.assertEqual(self.season.phase, 'Builds')  
        self.season.regress()
        self.assertEqual(self.season.phase, 'Retreats')
        self.season.regress()
        self.assertEqual(self.season.name, 'Fall')         

    def test_conclude(self):
        self.season.conclude()
        self.assertEqual(self.season.year, 1900) 
        self.assertEqual(self.season.phase, 'Postgame')  
        self.assertEqual(self.season.name, '-')      
   


if __name__ == '__main__':
    unittest.main()
