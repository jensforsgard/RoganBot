#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module to perform the DATC tests.
"""

import adjudicator.game as gm
import adjudicator.board as bd
import adjudicator.orders as od
import unittest

class TestAdjudicator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gameFvA = gm.Game('ClassicFvA', 'Test', 0)
        cls.game = gm.Game('Classic', 'Test', 0)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.gameFvA.reset()
        self.gameFvA.start()
        self.game.reset()
        self.game.start()

    def tearDown(self):
        pass

    def test_6_A_1(self):
        self.game.order('Brest move to North Sea')
        self.game.adjudicate()        
        self.assertIn('French Fleet in Brest move to North Sea (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_A_2(self):
        with self.assertRaises(ValueError):
            self.game.order('Marseilles move to Gulf of Lyon')

    def test_6_A_3(self):
        with self.assertRaises(ValueError):
            self.game.order('Trieste move to Tyrolia')

    def test_6_A_4(self):
        with self.assertRaises(gm.OrderInputError):
            self.game.order('Budapest move to Budapest')

    def test_6_A_5(self):
        with self.assertRaises(gm.OrderInputError):
            self.game.order('Marseilles move to Marseilles via convoy')

    def test_6_A_7(self):
        with self.assertRaises(gm.OrderInputError):
            self.gameFvA.add_unit('Fleet', 'Austria', 'Adriatic Sea')
            self.gameFvA.order('Trieste move to Apulia via Convoy')
            self.gameFvA.order('Adriatic Sea convoys Trieste move'
                                     ' to Apulia')

    def test_6_A_8(self):
        with self.assertRaises(gm.OrderInputError):
            self.game.order('Burgundy supports Burgundy holds')

    def test_6_A_9(self):
        self.gameFvA.add_unit('Fleet', 'France', 'Rome')
        self.gameFvA.order('Rome move to Venice')
        self.gameFvA.adjudicate()
        self.assertIn('French Fleet in Rome move to Venice (fails).', 
                      self.gameFvA.order_archive.loc(0))

    def test_6_A_10(self):
        self.gameFvA.add_unit('Fleet', 'France',  'Rome')
        self.gameFvA.add_unit('Army',  'France',  'Apulia')
        self.gameFvA.add_unit('Army',  'Austria', 'Venice')
        self.gameFvA.order('Venice H')
        self.gameFvA.order('Apulia move to Venice')
        self.gameFvA.order('Rome supports Apulia move to Venice')
        self.gameFvA.adjudicate()
        self.assertIn('French Fleet in Rome supports the move Apulia '
                      'to Venice (fails).', self.gameFvA.order_archive.loc(0))
        self.assertIn('French Army in Apulia move to Venice (fails).', 
                      self.gameFvA.order_archive.loc(0))

    def test_6_A_11(self):
        self.game.order('Marseilles move to Burgundy')
        self.game.order('Paris move to Burgundy')
        self.game.adjudicate()
        self.assertIn('French Army in Marseilles move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_A_12(self):
        self.game.order('Vienna move to Galicia')
        self.game.order('Budapest move to Galicia')
        self.game.order('Warsaw move to Galicia')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Budapest move to Galicia (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Vienna move to Galicia (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Warsaw move to Galicia (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_B_1(self):
        with self.assertRaises(bd.MapError):
            self.game.add_unit('Fleet', 'France',  'Portugal')
            self.game.order('Portugal move to Spain')

    def test_6_B_2(self):
        self.game.add_unit('Fleet', 'France',  'Gascony')
        self.game.order('Gascony move to Spain')
        self.game.adjudicate()
        self.assertIn('French Fleet in Gascony move to Spain (north coast)'
                      ' (succeeds).', self.game.order_archive.loc(0))

    def test_6_B_3(self):
        self.game.add_unit('Fleet', 'France',  'Gascony')
        self.game.order('Gascony move to Spain (south coast)')
        self.game.adjudicate()
        self.assertIn('French Fleet in Gascony move to Spain (north coast)'
                      ' (succeeds).', self.game.order_archive.loc(0))

    def test_6_B_4(self):
        self.game.add_unit('Fleet', 'France', 'Gulf of Lyon')
        self.game.add_unit('Fleet', 'France', 'Gascony')
        self.game.add_unit('Army', 'Austria', 'Spain')
        self.game.order('Gascony move to Spain (north coast)')
        self.game.order('GoL support move Gas to Spain (north coast)')
        self.game.order('Spain H')
        self.game.adjudicate()
        self.assertIn('French Fleet in Gascony move to Spain (north coast)'
                      ' (succeeds).', self.game.order_archive.loc(0))

    def test_6_B_5(self):
        self.game.add_unit('Fleet', 'Austria', 'Bulgaria (north coast)')
        self.game.add_unit('Army', 'Austria', 'Serbia')
        self.game.add_unit('Army', 'France', 'Greece')
        self.game.order('Serbia move to Greece')
        self.game.order('Bulgaria supports Serbia move to Greece')
        self.game.order('Greece H')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Bulgaria (north coast) supports '
                      'the move Serbia to Greece (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Serbia move to Greece (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_B_6(self):
        self.game.add_unit('Fleet', 'France', 'Irish Sea')
        self.game.add_unit('Fleet', 'France', 'North Atlantic Ocean')
        self.game.add_unit('Fleet', 'France', 'Gulf of Lyon')
        self.game.add_unit('Fleet', 'Austria', 'Spain (north coast)')
        self.game.add_unit('Fleet', 'Austria', 'Mid-Atlantic Ocean')
        self.game.order('North Atlantic Ocean move to MAO')
        self.game.order('Irish Sea supports NAO move to MAO')
        self.game.order('Spain supports Mid-Atlantic Ocean holds')
        self.game.order('Gulf of Lyon move to Spain (south coast)')
        self.game.order('Mid-Atlantic Ocean holds')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Spain (north coast) supports the '
                      'Fleet in Mid-Atlantic Ocean holds (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in North Atlantic Ocean move to '
                      'Mid-Atlantic Ocean (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_B_7(self):
        self.game.delete_unit('Constantinople')
        self.game.add_unit('Fleet', 'Austria', 'Black Sea')
        self.game.add_unit('Fleet', 'Austria', 'Constantinople')
        self.game.add_unit('Army', 'France', 'Bulgaria')
        self.game.order('Black Sea supports move Con to Bul')
        self.game.order('F Con - Bul (s)')
        self.game.adjudicate()
        self.assertEqual(len(self.game.orders), 1)
        self.assertTrue(isinstance(self.game.orders[0], od.Retreat))

    def test_6_B_8(self):
        self.game.add_unit('Fleet', 'Austria', 'Black Sea')
        self.game.add_unit('Army', 'England', 'Bulgaria')
        self.game.order('Black Sea move to Bulgaria')
        self.game.order('Constantinople supports move BLA to Bulgaria')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Black Sea move to Bulgaria '
                      '(north coast) (succeeds).', self.game.order_archive.loc(0))
        
    def test_6_B_9(self):
        self.game.add_unit('Fleet', 'France', 'Portugal')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'Austria', 'Gulf of Lyon')
        self.game.add_unit('Fleet', 'Austria', 'Western Mediterranean')
        self.game.order('Mid-Atlantic Ocean move to Spain (south coast)')
        self.game.order('Por supports move MAO to Spain (north coast)')
        self.game.order('Gulf of Lyon move to Spain (south coast)')
        self.game.order('WMS supports move GoL to Spain (south coast)')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Gulf of Lyon move to Spain '
                      '(south coast) (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Mid-Atlantic Ocean move to Spain '
                      '(south coast) (fails).', self.game.order_archive.loc(0))

    def test_6_B_10(self):
        self.game.add_unit('Fleet', 'Austria', 'Bulgaria (north coast)')
        self.game.order('Bulgaria (south coast) move to Black Sea')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Bulgaria (north coast) move to Black '
                      'Sea (succeeds).', self.game.order_archive.loc(0))

    def test_6_B_11(self):
        self.game.add_unit('Fleet', 'Austria', 'Bulgaria (north coast)')
        self.game.order('Bulgaria (south coast) move to Greece')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Bulgaria (north coast) move to '
                      'Greece (fails).', self.game.order_archive.loc(0))

    def test_6_B_12(self):
        self.game.add_unit('Army', 'Austria', 'Portugal')
        self.game.order('Portugal move to Spain (south coast)')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Portugal move to Spain (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_B_13(self):
        self.game.delete_unit('Constantinople')
        self.game.add_unit('Fleet', 'Austria', 'Constantinople')
        self.game.add_unit('Fleet', 'France', 'Bulgaria (north coast)')
        self.game.order('Constantinople move to Bulgaria (south coast)')
        self.game.order('Bulgaria move to Constantinople')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Constantinople move to Bulgaria '
                      '(south coast) (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Bulgaria (north coast) move to '
                      'Constantinople (fails).', self.game.order_archive.loc(0))

    def test_6_B_14(self):
        with self.assertRaises(bd.MapError):
            self.game.delete_unit('Saint Petersburg')
            self.game.adjudicate()
            self.game.adjudicate()
            self.game.order('Russian build 1 Fleet Saint Petersburg')

    def test_6_C_1(self):
        self.game.add_unit('Army', 'France', 'Galicia')
        self.game.order('Vienna move to Galicia')
        self.game.order('Galicia move to Budapest')
        self.game.order('Budapest move to Vienna')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Budapest move to Vienna (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Vienna move to Galicia (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Galicia move to Budapest (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_C_2(self):
        self.game.add_unit('Army', 'France', 'Galicia')
        self.game.order('Vienna move to Galicia')
        self.game.order('Galicia move to Budapest')
        self.game.order('Budapest move to Vienna')
        self.game.order('Warsaw supports move Vienna to Galicia.')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Budapest move to Vienna (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Vienna move to Galicia (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Galicia move to Budapest (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_C_3(self):
        self.game.add_unit('Army', 'France', 'Galicia')
        self.game.order('Vienna move to Galicia')
        self.game.order('Galicia move to Budapest')
        self.game.order('Budapest move to Vienna')
        self.game.order('Warsaw move to Galicia.')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Budapest move to Vienna (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Vienna move to Galicia (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Galicia move to Budapest (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_C_4(self):
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Army',  'Austria', 'Edinburgh')
        self.game.add_unit('Army',  'Austria', 'London')
        self.game.add_unit('Fleet', 'Austria', 'North Sea')
        self.game.add_unit('Army',  'France', 'Yorkshire')
        self.game.add_unit('Fleet', 'France', 'Denmark')
        self.game.order('Edinburgh move to London via convoy')
        self.game.order('Yorkshire move to Edinburgh')
        self.game.order('London move to Yorkshire')
        self.game.order('North sea convoy Edinburgh move to London')
        self.game.order('Denmark move to North Sea')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Edinburgh move via convoy to London '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in London move to Yorkshire (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Yorkshire move to Edinburgh '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_C_5(self):
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Army',  'Austria', 'Edinburgh')
        self.game.add_unit('Army',  'Austria', 'London')
        self.game.add_unit('Fleet', 'Austria', 'North Sea')
        self.game.add_unit('Army',  'France', 'Yorkshire')
        self.game.add_unit('Fleet', 'France', 'Norway')
        self.game.add_unit('Fleet', 'France', 'Denmark')
        self.game.order('Edinburgh move to London via convoy')
        self.game.order('Yorkshire move to Edinburgh')
        self.game.order('London move to Yorkshire')
        self.game.order('North sea convoy Edinburgh move to London')
        self.game.order('Denmark move to North Sea')
        self.game.order('Norway support move Denmark to North Sea')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Edinburgh move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in London move to Yorkshire (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Yorkshire move to Edinburgh (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Denmark move to North Sea (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_C_6(self):
        self.game.delete_unit('London')
        self.game.add_unit('Army', 'France', 'Belgium')
        self.game.add_unit('Army', 'Austria', 'London')
        self.game.add_unit('Fleet', 'Austria', 'North Sea')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.order('Belgium move to London via convoy')
        self.game.order('London move to Belgium via convoy')
        self.game.order('North sea convoy Belgium move to London')
        self.game.order('English Channel convoy London move to Belgium')
        self.game.adjudicate()
        self.assertIn('Austrian Army in London move via convoy to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Belgium move via convoy to London '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_C_7(self):
        self.game.delete_unit('London')
        self.game.add_unit('Army', 'France', 'London')
        self.game.add_unit('Army', 'Austria', 'Yorkshire')
        self.game.add_unit('Army', 'Austria', 'Belgium')
        self.game.add_unit('Fleet', 'Austria', 'North Sea')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.order('Belgium move to London via convoy')
        self.game.order('London move to Belgium via convoy')
        self.game.order('Yorkshire move to London')
        self.game.order('North sea convoy Belgium move to London')
        self.game.order('English Channel convoy London move to Belgium')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Yorkshire move to London (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Belgium move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in London move via convoy to Belgium '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_D_1(self):
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy holds')
        self.game.order('Munich supports Burgundy holds')
        self.game.adjudicate()
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_2(self):
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.add_unit('Army', 'France', 'Silesia')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy holds')
        self.game.order('Munich supports Burgundy holds')
        self.game.order('Silesia move to Munich')
        self.game.adjudicate()
        self.assertIn('French Army in Paris move to Burgundy (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('German Army in Munich supports the Army in Burgundy '
                      'holds (fails).', self.game.order_archive.loc(0))

    def test_6_D_3(self):
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.add_unit('Army', 'Austria', 'Spain')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy holds')
        self.game.order('Spain move to Marseilles')
        self.game.adjudicate()
        self.assertIn('French Army in Marseilles supports the move Paris '
                      'to Burgundy (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_4(self):
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy support hold Munich')
        self.game.order('Munich support hold Burgundy')
        self.game.adjudicate()
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_5(self):
        self.game.delete_unit('Kiel')
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.add_unit('Army', 'Austria', 'Kiel')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy support Kiel move to Ruhr')
        self.game.order('Munich support hold Burgundy')
        self.game.order('Kiel move to Ruhr')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Burgundy supports the move Kiel '
                      'to Ruhr (fails).', self.game.order_archive.loc(0))
        self.assertIn('German Army in Munich supports the Army in Burgundy '
                      'holds (succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_6(self):
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Army', 'Austria', 'Belgium')
        self.game.add_unit('Fleet', 'Austria', 'English Channel')
        self.game.add_unit('Fleet', 'Austria', 'North Sea')
        self.game.order('Brest move to English Channel')
        self.game.order('Mid-Atlantic Ocean supports Brest move to ENG')
        self.game.order('English Channel convoy Belgium to London')
        self.game.order('Belgium move to London via convoy')
        self.game.order('North Sea supports English Channel holds')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in North Sea supports the Fleet in '
                      'English Channel holds (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Brest move to English Channel (fails).',
                      self.game.order_archive.loc(0))

    def test_6_D_7(self):
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.add_unit('Army', 'Austria', 'Ruhr')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles support move Paris to Burgundy')
        self.game.order('Burgundy move to Munich')
        self.game.order('Ruhr supports Burgundy holds')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Ruhr supports the Army in Burgundy '
                      'holds (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_D_8(self):
        self.game.delete_unit('London')
        self.game.add_unit('Army',  'Austria', 'London')
        self.game.add_unit('Army',  'France',  'Yorkshire')
        self.game.add_unit('Army',  'France',  'Wales')
        self.game.add_unit('Fleet', 'Austria', 'North Sea')
        self.game.add_unit('Fleet', 'Austria', 'English Channel')
        self.game.order('London move to Belgium via convoy')
        self.game.order('Yorkshire move to London')
        self.game.order('Wales supports Yorkshire move to London')
        self.game.order('North Sea S London H')
        self.game.adjudicate()
        # Explicit convoying
        # self.assertIn('Austrian Army in London move via convoy to Belgium '
        #               '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in London move to Belgium '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Yorkshire move to London (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Fleet in North Sea supports the Army in '
                      'London holds (fails).', self.game.order_archive.loc(0))

    def test_6_D_9(self):
        self.game.add_unit('Army',  'Austria', 'Burgundy')
        self.game.add_unit('Army',  'Austria', 'Picardy')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy H')
        self.game.order('Picardy supports Burgundy move to Paris')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Picardy supports the move '
                      'Burgundy to Paris (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_D_10(self):
        self.game.add_unit('Army',  'France', 'Burgundy')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.adjudicate()
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_11(self):
        self.game.delete_unit('Munich')
        self.game.add_unit('Army',  'France', 'Burgundy')
        self.game.add_unit('Army',  'Austria', 'Silesia')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy move to Munich')
        self.game.order('Silesia move to Munich')
        self.game.adjudicate()
        self.assertIn('French Army in Burgundy move to Munich (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_12(self):
        self.game.add_unit('Army',  'France', 'Burgundy')
        self.game.add_unit('Army',  'Austria', 'Gascony')
        self.game.order('Gascony move to Burgundy')
        self.game.order('Marseilles supports Gascony move to Burgundy')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Gascony move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_13(self):
        self.game.delete_unit('Munich')
        self.game.add_unit('Army',  'France', 'Burgundy')
        self.game.add_unit('Army',  'Austria', 'Gascony')
        self.game.add_unit('Army',  'Austria', 'Silesia')
        self.game.order('Gascony move to Burgundy')
        self.game.order('Marseilles supports Gascony move to Burgundy')
        self.game.order('Burgundy move to Munich')
        self.game.order('Silesia move to Munich')
        self.game.adjudicate()
        self.assertIn('French Army in Burgundy move to Munich (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Gascony move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_D_14(self):
        self.game.delete_unit('Munich')
        self.game.add_unit('Army',  'France', 'Burgundy')
        self.game.add_unit('Army',  'Austria', 'Gascony')
        self.game.add_unit('Army',  'Austria', 'Silesia')
        self.game.add_unit('Army',  'Austria', 'Picardy')
        self.game.order('Gascony move to Burgundy')
        self.game.order('Marseilles supports Gascony move to Burgundy')
        self.game.order('Picardy supports Gascony move to Burgundy')
        self.game.order('Burgundy move to Munich')
        self.game.order('Silesia move to Munich')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Gascony move to Burgundy (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_D_15(self):
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.order('Burgundy move to Marseilles')
        self.game.adjudicate()
        self.assertIn('French Army in Paris move to Burgundy (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_D_16(self):
        self.game.delete_unit('London')
        self.game.add_unit('Army',  'Austria', 'London')
        self.game.add_unit('Army',  'Austria', 'Holland')
        self.game.add_unit('Army',  'France', 'Belgium')
        self.game.add_unit('Fleet',  'France', 'English Channel')
        self.game.order('London move to Belgium via convoy')
        self.game.order('Holland supports move London to Belgium')
        self.game.order('English Channel convoys move London to Belgium')
        self.game.adjudicate()
        self.assertIn('Austrian Army in London move via convoy to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Fleet in English Channel convoys London to '
                      'Belgium (succeeds).', self.game.order_archive.loc(0))

    def test_6_D_17(self):
        self.game.delete_unit('Ankara')
        self.game.delete_unit('Constantinople')
        self.game.delete_unit('Smyrna')
        self.game.add_unit('Fleet', 'Austria', 'Constantinople')
        self.game.add_unit('Fleet', 'Austria', 'Black Sea')
        self.game.add_unit('Army',  'France', 'Smyrna')
        self.game.add_unit('Army',  'France', 'Armenia')
        self.game.add_unit('Fleet', 'France', 'Ankara')
        self.game.order('Black Sea move to Ankara')
        self.game.order('Constantinople supports Black Sea - Ankara')
        self.game.order('Ankara move to Constantinople')
        self.game.order('Armenia move to Ankara')
        self.game.order('Smyrna supports Ankara move to Constantinople')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Black Sea move to Ankara (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Ankara move to Constantinople '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_D_18(self):
        self.game.delete_unit('Ankara')
        self.game.delete_unit('Constantinople')
        self.game.delete_unit('Smyrna')
        self.game.add_unit('Army',  'Austria', 'Bulgaria')
        self.game.add_unit('Fleet', 'Austria', 'Constantinople')
        self.game.add_unit('Fleet', 'Austria', 'Black Sea')
        self.game.add_unit('Army',  'France', 'Smyrna')
        self.game.add_unit('Army',  'France', 'Armenia')
        self.game.add_unit('Fleet', 'France', 'Ankara')
        self.game.order('Black Sea move to Ankara')
        self.game.order('Constantinople supports Black Sea - Ankara')
        self.game.order('Ankara move to Constantinople')
        self.game.order('Armenia move to Ankara')
        self.game.order('Smyrna supports Ankara move to Constantinople')
        self.game.order('Bulgaria supports Constantinople holds')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Black Sea move to Ankara (succeeds).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Ankara move to Constantinople (fails).',
                      self.game.order_archive.loc(0))

    def test_6_D_19(self):
        self.game.delete_unit('Ankara')
        self.game.delete_unit('Constantinople')
        self.game.delete_unit('Smyrna')
        self.game.add_unit('Fleet', 'Austria', 'Constantinople')
        self.game.add_unit('Fleet', 'Austria', 'Black Sea')
        self.game.add_unit('Army',  'Austria', 'Smyrna')
        self.game.add_unit('Fleet', 'France', 'Ankara')
        self.game.order('Black Sea move to Ankara')
        self.game.order('Constantinople supports Black Sea - Ankara')
        self.game.order('Ankara move to Constantinople')
        self.game.order('Smyrna supports Ankara move to Constantinople')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Black Sea move to Ankara (succeeds).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Ankara move to Constantinople (fails).',
                      self.game.order_archive.loc(0))

    def test_6_D_20(self):
        self.game.add_unit('Army', 'France',  'Gascony')
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports move Paris to Burgundy')
        self.game.order('Gascony move to Marseilles')
        self.game.adjudicate()
        self.assertIn('French Army in Paris move to Burgundy (succeeds).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Marseilles supports the move Paris '
                      'to Burgundy (succeeds).', self.game.order_archive.loc(0))

    def test_6_D_21(self):
        self.game.add_unit('Army', 'Austria', 'Gascony')
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.add_unit('Army', 'France', 'Spain')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports move Paris to Burgundy')
        self.game.order('Gascony move to Marseilles')
        self.game.order('Brest move to Gascony')
        self.game.order('Spain supports move Brest to Gascony')
        self.game.adjudicate()
        self.assertIn('French Army in Marseilles supports the move Paris '
                      'to Burgundy (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Brest move to Gascony (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_D_22(self):
        with self.assertRaises(ValueError):
            self.game.delete_unit('Paris')
            self.game.add_unit('Army', 'Austria', 'Gascony')
            self.game.add_unit('Army', 'Austria', 'Paris')
            self.game.add_unit('Army', 'France', 'Picardy')
            self.game.order('Picardy supports move Brest to Paris')
            self.game.order('Brest move to Paris')
            self.game.order('Paris move to Brest')
            self.game.order('Gascony supports move Paris to Brest')
            self.game.adjudicate()

    def test_6_D_23(self):
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Marseilles')
        self.game.add_unit('Fleet', 'France', 'Spain (north coast)')
        self.game.add_unit('Fleet', 'Austria', 'Gulf of Lyon')
        self.game.add_unit('Fleet', 'Austria', 'Western Mediterranean')
        self.game.order('Gulf of Lyon move to Spain (south coast)')
        self.game.order('WMS supports GoL move to Spain (south coast)')
        self.game.order('Spain move to Gulf of Lyon')
        self.game.order('Marseilles supports Spain move to Gulf of Lyon')
        self.game.adjudicate()
        self.assertIn('French Fleet in Spain (north coast) move to Gulf of '
                      'Lyon (fails).', self.game.order_archive.loc(0))
        self.assertIn('Austrian Fleet in Gulf of Lyon move to Spain (south '
                      'coast) (succeeds).', self.game.order_archive.loc(0))

    def test_6_D_24(self):
        with self.assertRaises(ValueError):
            self.game.add_unit('Fleet', 'France', 'Spain (south coast)')
            self.game.add_unit('Fleet', 'France', 'Tyrrhenian Sea')
            self.game.add_unit('Fleet', 'France', 'Western Mediterranean')
            self.game.add_unit('Fleet', 'Austria', 'Gulf of Lyon')
            self.game.order('Spain supports Marseilles move to GoL')
            self.game.order('Marseilles move to Gulf of Lyon')
            self.game.order('Tyrrhenian Sea move to Gulf of Lyon')
            self.game.order('WMS supports Tyrrhenian Sea move to GoL')
            self.game.adjudicate()

    def test_6_D_25(self):
        self.game.add_unit('Army', 'France', 'Burgundy')
        self.game.add_unit('Army', 'Austria', 'Piedmont')
        self.game.add_unit('Army', 'Austria', 'Gascony')
        self.game.order('Marseilles supports Piedmont hold')
        self.game.order('Burgundy supports Marseilles hold')
        self.game.order('Piedmont move to Marseilles')
        self.game.order('Gascony supports move Piedmont to Marseilles')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Piedmont move to Marseilles (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Burgundy supports the Army in Marseilles'
                      ' holds (succeeds).', self.game.order_archive.loc(0))

    def test_6_D_26(self):
        self.game.add_unit('Army', 'France', 'Burgundy')
        self.game.add_unit('Army', 'Austria', 'Piedmont')
        self.game.add_unit('Army', 'Austria', 'Gascony')
        self.game.order('Marseilles supports Gascony move to Burgundy')
        self.game.order('Burgundy supports Marseilles hold')
        self.game.order('Piedmont move to Marseilles')
        self.game.order('Gascony supports move Piedmont to Marseilles')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Piedmont move to Marseilles (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Burgundy supports the Army in Marseilles'
                      ' holds (succeeds).', self.game.order_archive.loc(0))

    def test_6_D_27(self):
        self.game.delete_unit('Berlin')
        self.game.add_unit('Army', 'France', 'Berlin')
        self.game.add_unit('Fleet', 'France', 'Baltic Sea')
        self.game.add_unit('Fleet', 'France', 'Prussia')
        self.game.add_unit('Fleet', 'Austria', 'Denmark')
        self.game.add_unit('Fleet', 'Austria', 'Sweden')
        self.game.order('Sweden move to Baltic Sea')
        self.game.order('Denmark supports move Sweden to Baltic Sea')
        self.game.order('Berlin holds')
        self.game.order('Baltic Sea convoys Berlin to Livonia')
        self.game.order('Prussia supports Baltic Sea holds')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Sweden move to Baltic Sea (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Baltic Sea convoys Berlin to '
                      'Livonia (fails).', self.game.order_archive.loc(0))

    def test_6_D_28(self):
        self.game.add_unit('Army', 'Austria', 'Burgundy')
        self.game.order('Burgundy move to Moscow')
        self.game.order('Munich supports Burgundy holds')
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles supports Paris move to Burgundy')
        self.game.adjudicate()
        self.assertIn('Austrian Army in Burgundy move to Moscow (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Burgundy (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_D_29(self):
        self.game.add_unit('Army', 'France', 'Burgundy')
        self.game.add_unit('Fleet', 'Austria', 'Gascony')
        self.game.add_unit('Fleet', 'Italy', 'Spain (south coast)')
        self.game.order('Burgundy S Gascony H')
        self.game.order('Paris - Gascony')
        self.game.order('Marseilles S Paris - Gascony')
        self.game.order('Gascony - Spain (south coast)')
        self.game.adjudicate()
        self.assertIn('Austrian Fleet in Gascony move to Spain (north '
                      'coast) (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Gascony (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_D_30(self):
        with self.assertRaises(bd.MapError):
            self.game.delete_unit('Constantinople')
            self.game.add_unit('Fleet', 'Austria', 'Aegean Sea')
            self.game.add_unit('Fleet', 'Austria', 'Constantinople')
            self.game.add_unit('Fleet', 'France', 'Black Sea')
            self.game.add_unit('Fleet', 'France', 'Bulgaria')
            self.game.order('Aegean Sea S Constantinople H')
            self.game.order('Constantinople - Bulgaria')
            self.game.order('Black Sea - Constantinople')
            self.game.order('Bulgaria S Black Sea - Constantinople')
            self.game.adjudicate()

    def test_6_D_31(self):
        self.game.delete_unit('Ankara')
        self.game.add_unit('Army', 'Austria', 'Rumania')
        self.game.add_unit('Fleet', 'Austria', 'Black Sea')
        self.game.add_unit('Army', 'France', 'Ankara')
        self.game.order('Rumania move to Armenia via convoy')
        self.game.order('Black Sea supports move Rumania to Armenia')
        self.game.order('Ankara move to Armenia')
        self.game.adjudicate()
        # Explicit convoy rule
        # self.assertIn('Austrian Army in Rumania move via convoy to Armenia '
        #               '(fails).', self.game.order_archive.loc(0))
        # webDip rule adjustment
        self.assertIn('Austrian Army in Rumania move to Armenia '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Ankara move to Armenia (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_D_32(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('Edinburgh')
        self.game.delete_unit('London')
        self.game.add_unit('Army', 'Austria', 'Liverpool')
        self.game.add_unit('Fleet', 'Austria', 'Edinburgh')
        self.game.add_unit('Fleet', 'France', 'London')
        self.game.add_unit('Army', 'France', 'Yorkshire')
        self.game.order('Edinburgh S Liverpool - Yorkshire')
        self.game.order('Liverpool - Yorkshire')
        self.game.order('London S Yorkshire H')
        self.game.order('Yorkshire - Holland')
        self.game.adjudicate()
        self.assertIn('French Army in Yorkshire move to Holland (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in London supports the Army in Yorkshire '
                      'holds (fails).', self.game.order_archive.loc(0))
        self.assertIn('Austrian Army in Liverpool move to Yorkshire '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_D_33(self):
        self.game.order('Paris move to Burgundy')
        self.game.order('Marseilles move to Burgundy')
        self.game.order('Munich supports Marseilles move to Burgundy')
        self.game.adjudicate()
        self.assertIn('French Army in Marseilles move to Burgundy (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_D_34(self):
        with self.assertRaises(gm.OrderInputError):
            self.game.add_unit('Army', 'Austria', 'Burgundy')
            self.game.order('Paris supports move Burgundy to Paris')
            self.game.adjudicate()

    def test_6_E_1(self):
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Silesia')
        self.game.add_unit('Army', 'Russia', 'Prussia')
        self.game.order('Berlin move to Prussia')
        self.game.order('Kiel move to Berlin')
        self.game.order('Silesia supports move Berlin to Prussia')
        self.game.order('Prussia move to Berlin ')
        self.game.adjudicate()
        self.assertIn('Russian Army in Prussia move to Berlin (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('German Army in Berlin move to Prussia (succeeds).', 
                      self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Kiel move to Berlin (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_E_2(self):
        self.game.order('Berlin move to Kiel')
        self.game.order('Kiel move to Berlin')
        self.game.order('Munich supports move Berlin to Kiel')
        self.game.adjudicate()
        self.assertIn('German Army in Berlin move to Kiel (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Kiel move to Berlin (fails).',
                      self.game.order_archive.loc(0))

    def test_6_E_3(self):
        self.game.delete_unit('Kiel')
        self.game.add_unit('Fleet', 'Italy', 'Kiel')
        self.game.order('Berlin move to Kiel')
        self.game.order('Kiel move to Berlin')
        self.game.order('Munich supports move Kiel to Berlin')
        self.game.adjudicate()
        self.assertIn('German Army in Berlin move to Kiel (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('Italian Fleet in Kiel move to Berlin (fails).',
                      self.game.order_archive.loc(0))

    def test_6_E_4(self):
        self.game.add_unit('Fleet', 'Austria', 'Holland')
        self.game.add_unit('Fleet', 'Austria', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Austria', 'Skagerrack')
        self.game.add_unit('Fleet', 'France', 'North Sea')
        self.game.add_unit('Fleet', 'France', 'Belgium')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.add_unit('Fleet', 'England', 'Norwegian Sea')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Kiel')
        self.game.add_unit('Army', 'Germany', 'Ruhr')
        self.game.order('Holland move to North Sea')
        self.game.order('Heligoland Bight supports move Holland to NTH')
        self.game.order('Skagerrack supports move Holland to North Sea')
        self.game.order('North Sea move to Holland')
        self.game.order('Belgium supports move North Sea to Holland')
        self.game.order('Yorkshire supports move Norwegian Sea to NTH')
        self.game.order('Edinburgh supports move Norwegian Sea to NTH')
        self.game.order('Norwegian Sea move to North Sea')
        self.game.order('Kiel supports Ruhr move to Holland')
        self.game.order('Ruhr move to Holland')
        self.game.adjudicate()
        self.assertIn('German Army in Ruhr move to Holland (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Fleet in Holland move to North Sea (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('English Fleet in Norwegian Sea move to North Sea '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Fleet in North Sea move to Holland (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_E_5(self):
        self.game.add_unit('Fleet', 'Austria', 'Holland')
        self.game.add_unit('Fleet', 'Austria', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Austria', 'Skagerrack')
        self.game.add_unit('Fleet', 'France', 'North Sea')
        self.game.add_unit('Fleet', 'France', 'Belgium')
        self.game.delete_unit('Liverpool')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.add_unit('Fleet', 'England', 'Norwegian Sea')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Kiel')
        self.game.add_unit('Army', 'Germany', 'Ruhr')
        self.game.order('Holland move to North Sea')
        self.game.order('Heligoland Bight supports move Holland to NTH')
        self.game.order('Skagerrack supports move Holland to NTH')
        self.game.order('North Sea move to Holland')
        self.game.order('Belgium supports move North Sea to Holland')
        self.game.order('Yorkshire supports move Norwegian Sea to NTH')
        self.game.order('London supports move Norwegian Sea to NTH')
        self.game.order('Edinburgh supports move Norwegian Sea to NTH')
        self.game.order('Norwegian Sea move to North Sea')
        self.game.order('Kiel supports Ruhr move to Holland')
        self.game.order('Ruhr move to Holland')
        self.game.adjudicate()
        self.assertIn('German Army in Ruhr move to Holland (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Fleet in Holland move to North Sea (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_E_6(self):
        self.game.add_unit('Fleet', 'Austria', 'Holland')
        self.game.add_unit('Fleet', 'Austria', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'France', 'North Sea')
        self.game.add_unit('Fleet', 'France', 'Belgium')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Kiel')
        self.game.add_unit('Army', 'Germany', 'Ruhr')
        self.game.order('Holland move to North Sea')
        self.game.order('Heligoland Bight supports move Holland to NTH')
        self.game.order('North Sea move to Holland')
        self.game.order('Belgium supports move North Sea to Holland')
        self.game.order('English Channel supports move Holland to NTH')
        self.game.order('Kiel supports Ruhr move to Holland')
        self.game.order('Ruhr move to Holland')
        self.game.adjudicate()
        self.assertIn('German Army in Ruhr move to Holland (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Austrian Fleet in Holland move to North Sea (fails).',
                      self.game.order_archive.loc(0))

    def test_6_E_7(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Holland')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Russia', 'Skagerrack')
        self.game.add_unit('Fleet', 'Russia', 'Norway')
        self.game.order('North Sea Holds')
        self.game.order('Yorkshire supports move Norway to North Sea')
        self.game.order('Heligoland Bight move to North Sea')
        self.game.order('Holland supports Heligoland Bight move to NTH')
        self.game.order('Norway move to North Sea')
        self.game.order('Skagerrack supports Norway move to North Sea')
        self.game.adjudicate()
        self.assertIn('German Fleet in Heligoland Bight move to North Sea '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in Norway move to North Sea (fails).',
                      self.game.order_archive.loc(0))

    def test_6_E_8(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Holland')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Fleet', 'Russia', 'Skagerrack')
        self.game.add_unit('Fleet', 'Russia', 'Norway')
        self.game.order('North Sea move to Norway')
        self.game.order('Yorkshire supports move Norway to North Sea')
        self.game.order('Heligoland Bight move to North Sea')
        self.game.order('Holland supports Heligoland Bight move to NTH')
        self.game.order('Norway move to North Sea')
        self.game.order('Skagerrack supports Norway move to North Sea')
        self.game.adjudicate()
        self.assertIn('English Fleet in North Sea move to Norway (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Heligoland Bight move to North Sea '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in Norway move to North Sea (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_E_9(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Holland')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Fleet', 'Russia', 'Skagerrack')
        self.game.add_unit('Fleet', 'Russia', 'Norway')
        self.game.order('North Sea move to Norwegian Sea')
        self.game.order('Yorkshire supports move Norway to North Sea')
        self.game.order('Heligoland Bight move to North Sea')
        self.game.order('Holland supports Heligoland Bight move to NTH')
        self.game.order('Norway move to North Sea')
        self.game.order('Skagerrack supports Norway move to North Sea')
        self.game.adjudicate()
        self.assertIn('English Fleet in North Sea move to Norwegian Sea '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in Norway move to North Sea (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_E_10(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Holland')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Germany', 'Denmark')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Fleet', 'Russia', 'Skagerrack')
        self.game.add_unit('Fleet', 'Russia', 'Norway')
        self.game.order('North Sea move to Denmark')
        self.game.order('Yorkshire supports move Norway to North Sea')
        self.game.order('Heligoland Bight move to North Sea')
        self.game.order('Holland supports Heligoland Bight move to NTH')
        self.game.order('Denmark move to Heligoland Bight')
        self.game.order('Skagerrack supports Norway move to North Sea')
        self.game.order('Norway move to North Sea')
        self.game.adjudicate()
        self.assertIn('English Fleet in North Sea move to Denmark (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Heligoland Bight move to North Sea '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Denmark move to Heligoland Bight '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in Norway move to North Sea (fails).',
                      self.game.order_archive.loc(0))

    def test_6_E_11(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.add_unit('Army', 'France', 'Gascony')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Spain')
        self.game.add_unit('Fleet', 'Germany', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'Germany', 'Gulf of Lyon')        
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Portugal')
        self.game.add_unit('Fleet', 'Italy', 'Western Mediterranean')
        self.game.order('Spain move to Portugal via convoy')
        self.game.order('Mid-Atlantic Ocean convoy Spain to Portugal')
        self.game.order('Gulf of Lyon supports Por move to Spain (n)')
        self.game.order('Gascony move to Spain')
        self.game.order('Marseilles supports Gascony move to Spain')
        self.game.order(' Por - Spa (n)')
        self.game.order('WMS supports Por move to Spain (n)')
        self.game.adjudicate()
        self.assertIn('French Army in Gascony move to Spain (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('German Army in Spain move via convoy to Portugal '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('Italian Fleet in Portugal move to Spain (north coast) '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_E_12(self):
        self.game.delete_unit('Trieste')
        self.game.delete_unit('Vienna')
        self.game.add_unit('Army', 'Austria', 'Serbia')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Army', 'Italy', 'Vienna')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Galicia')
        self.game.add_unit('Army', 'Russia', 'Rumania')
        self.game.order('Budapest move to Rumania')
        self.game.order('Serbia supports Vienna move to Budapest')
        self.game.order('Vienna move to Budapest')
        self.game.order('Galicia move to Budapest')
        self.game.order('Rumania supports Galicia move to Budapest')
        self.game.adjudicate()
        self.assertIn('Russian Army in Galicia move to Budapest (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_E_13(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Belgium')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'North Sea')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Fleet', 'Russia', 'Norwegian Sea')
        self.game.add_unit('Fleet', 'Russia', 'Norway')
        self.game.order('Yorkshire move to North Sea')
        self.game.order('Edinburgh supports Yorkshire move to NTH')
        self.game.order('Belgium move to North Sea')
        self.game.order('English Channel supports Belgium move to NTH')
        self.game.order('Norwegian Sea move to North Sea')
        self.game.order('Norway supports Norwegian Sea move to NTH')
        self.game.adjudicate()
        self.assertIn('English Fleet in Yorkshire move to North Sea (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Belgium move to North Sea (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in Norwegian Sea move to North Sea '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_E_14(self):
        self.game.delete_unit('Edinburgh')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Fleet', 'Russia', 'Edinburgh')
        self.game.order('Edinburgh move to Liverpool')
        self.game.order('Liverpool move to Edinburgh')
        self.game.adjudicate()
        self.assertIn('English Army in Liverpool move to Edinburgh (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in Edinburgh move to Liverpool (fails).',
                      self.game.order_archive.loc(0))

    def test_6_E_15(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Holland')
        self.game.add_unit('Army', 'England', 'Ruhr')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Denmark')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Army', 'Italy', 'Kiel')
        self.game.add_unit('Army', 'Italy', 'Munich')
        self.game.add_unit('Army', 'Italy', 'Silesia')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Prussia')
        self.game.add_unit('Fleet', 'Russia', 'Baltic Sea')
        self.game.order('Ruhr move to Kiel')
        self.game.order('Holland supports Ruhr move to Kiel')
        self.game.order('Kiel move to Berlin')
        self.game.order('Munich supports Kiel move to Berlin')
        self.game.order('Silesia supports Kiel move to Berlin')
        self.game.order('Berlin move to Kiel')
        self.game.order('Denmark supports Berlin move to Kiel')
        self.game.order('Heligoland Bight supports Berlin move to Kiel')
        self.game.order('Prussia move to Berlin')
        self.game.order('Baltic Sea supports Prussia move to Berlin')
        self.game.adjudicate()
        self.assertIn('English Army in Ruhr move to Kiel (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('German Army in Berlin move to Kiel (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Italian Army in Kiel move to Berlin (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Prussia move to Berlin (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_F_1(self):
        with self.assertRaises(gm.OrderInputError):
            self.game.delete_unit('Ankara')
            self.game.delete_unit('Constantinople')
            self.game.delete_unit('Smyrna')
            self.game.add_unit('Fleet', 'Turkey', 'Constantinople')
            self.game.add_unit('Fleet', 'Turkey', 'Aegean Sea')
            self.game.add_unit('Fleet', 'Turkey', 'Black Sea')
            self.game.add_unit('Army', 'Turkey', 'Ankara')
            self.game.order('Ankara move to Greece via convoy')
            self.game.order('Black Sea convoy Ankara move to Greece')
            self.game.order('Constantinople convoy Ankara move to Gre')
            self.game.order('Aegean Sea convoy Ankara move to Greece')
            self.game.adjudicate()

    def test_6_F_2(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Marseilles')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Army', 'England', 'London')
        self.game.order('London move to Brest via convoy')
        self.game.order('English Channel convoy London move to Brest')
        self.game.order('Paris move to Brest')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Brest '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Brest (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_F_3(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Army', 'England', 'London')
        self.game.order('London move to Brest via convoy')
        self.game.order('English Channel convoy London move to Brest')
        self.game.order('Mid-Atlantic Ocean supports London move to Bre')
        self.game.order('Paris move to Brest')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Brest '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Paris move to Brest (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_F_4(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'North Sea')
        self.game.order('London move to Brest via convoy')
        self.game.order('English Channel convoy London move to Brest')
        self.game.order('North Sea move to English Channel')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Brest '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_5(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Fleet', 'France', 'Belgium')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Skagerrack')
        self.game.add_unit('Fleet', 'Germany', 'Denmark')
        self.game.order('London move to Holland via convoy')
        self.game.order('North Sea convoy London move to Holland')
        self.game.order('English Channel move to North Sea')
        self.game.order('Belgium supports English Channel move to NTH')
        self.game.order('Skagerrack move to North Sea')
        self.game.order('Denmark supports Skagerrack move to North Sea')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Holland '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_6(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Army', 'France', 'Picardy')
        self.game.add_unit('Army', 'France', 'Burgundy')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Holland')
        self.game.add_unit('Army', 'Germany', 'Belgium')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Germany', 'Skagerrack')
        self.game.order('London move to Holland via convoy')
        self.game.order('North Sea convoy London move to Holland')
        self.game.order('Holland supports Belgium holds')
        self.game.order('Belgium supports Holland holds')
        self.game.order('HEL supports Skagerrack move to NTH')
        self.game.order('Skagerrack move to North Sea')
        self.game.order('Picardy move to Belgium')
        self.game.order('Burgundy supports Picardy move to Belgium')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Holland '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Skagerrack move to North Sea '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('German Army in Holland supports the Army in Belgium '
                      'holds (succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Picardy move to Belgium (fails).', 
                      self.game.order_archive.loc(0))


    def test_6_F_7(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Germany', 'Skagerrack')
        self.game.order('London move to Holland via convoy')
        self.game.order('North Sea convoy London move to Holland')
        self.game.order('Skagerrack move to North Sea')
        self.game.order('Heligoland Bight supports SKA move to NTH')
        self.game.adjudicate()
        self.game.order('North Sea retreats to Holland')
        self.game.adjudicate()
        self.assertIn('The Fleet in North Sea retreats to Holland.', 
                      self.game.order_archive.loc(1))

    def test_6_F_8(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Belgium')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Germany', 'Skagerrack')
        self.game.order('London move to Holland via convoy')
        self.game.order('North Sea convoy London move to Holland')
        self.game.order('Skagerrack move to North Sea')
        self.game.order('Heligoland Bight supports SKA move to NTH')
        self.game.order('Belgium move to Holland')
        self.game.adjudicate()
        self.assertIn('German Army in Belgium move to Holland (succeeds).', 
                      self.game.order_archive.loc(0))

    def test_6_F_9(self):
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.order('London move to Belgium via convoy')
        self.game.order('North Sea convoy London move to Belgium')
        self.game.order('English Channel convoy London move to Belgium')
        self.game.order('Mid-Atlantic Ocean move to English Channel')
        self.game.order('Brest supports move Mid-Atlantic Ocean to ENG')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_10(self):
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'English Channel')
        self.game.order('London move to Belgium via convoy')
        self.game.order('North Sea convoy London move to Belgium')
        self.game.order('English Channel convoy London move to Belgium')
        self.game.order('Mid-Atlantic Ocean move to English Channel')
        self.game.order('Brest supports move Mid-Atlantic Ocean to ENG')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_11(self):
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'English Channel')
        self.game.add_unit('Fleet', 'Russia', 'North Sea')
        self.game.order('London move to Belgium via convoy')
        self.game.order('North Sea convoy London move to Belgium')
        self.game.order('English Channel convoy London move to Belgium')
        self.game.order('Mid-Atlantic Ocean move to English Channel')
        self.game.order('Brest supports move Mid-Atlantic Ocean to ENG')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_12(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'France', 'North Atlantic Ocean')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Fleet', 'England', 'Irish Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.order('London move to Belgium via convoy')
        self.game.order('Irish Sea convoy London move to Belgium')
        self.game.order('English Channel convoy London move to Belgium')
        self.game.order('Mid-Atlantic Ocean move to Irish Sea')
        self.game.order('North Atlantic Ocean supports move MAO to IRI')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_13(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Holland')
        self.game.add_unit('Fleet', 'Germany', 'Denmark')
        self.game.order('London move to Belgium via convoy')
        self.game.order('North Sea convoy London move to Belgium')
        self.game.order('English Channel convoy London move to Belgium')
        self.game.order('Denmark move to North Sea')
        self.game.order('Holland supports Denmark move to North Sea')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))
        
    def test_6_F_14(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Wales')
        self.game.order('Wales move to English Channel')
        self.game.order('London supports move Wales to English Channel')
        self.game.order('Brest move to London via convoy')
        self.game.order('English Channel convoys Brest move to London')
        self.game.adjudicate()
        self.assertIn('English Fleet in Wales move to English Channel '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_15(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Wales')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Irish Sea')
        self.game.add_unit('Fleet', 'Italy', 'Mid-Atlantic Ocean')
        self.game.add_unit('Army', 'Italy', 'North Africa')
        self.game.order('Wales move to English Channel')
        self.game.order('London supports move Wales to ENG')
        self.game.order('Brest move to London via convoy')
        self.game.order('English Channel convoys Brest move to London')
        self.game.order('Irish Sea convoys North Africa to Wales')
        self.game.order('Mid-Atlantic Ocean convoys North Africa to Wal')
        self.game.order('North Africa move to Wales via convoy')
        self.game.adjudicate()
        self.assertIn('English Fleet in Wales move to English Channel '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('Italian Army in North Africa move via convoy to Wales '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_F_16(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Wales')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'North Sea')
        self.game.add_unit('Fleet', 'Germany', 'Belgium')
        self.game.order('Wales move to English Channel')
        self.game.order('London supports move Wales to English Channel')
        self.game.order('Brest move to London via convoy')
        self.game.order('English Channel convoys Brest move to London')
        self.game.order('Belgium move to English Channel')
        self.game.order('North Sea supports Belgium move to ENG')
        self.game.adjudicate()
        self.assertIn('English Fleet in Wales move to English Channel '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Brest move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Belgium move to English Channel '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_F_17(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Yorkshire')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Wales')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'North Sea')
        self.game.add_unit('Fleet', 'Germany', 'Belgium')
        self.game.order('Wales move to English Channel')
        self.game.order('London supports move Wales to ENG')
        self.game.order('Brest move to London via convoy')
        self.game.order('English Channel convoys Brest move to London')
        self.game.order('Belgium move to English Channel')
        self.game.order('North Sea supports Belgium move to ENG')
        self.game.order('Yorkshire supports Brest move to London')
        self.game.adjudicate()
        self.assertIn('English Fleet in Wales move to English Channel '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Brest move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Belgium move to English Channel '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_F_18(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Belgium')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'London')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'Germany', 'Skagerrack')
        self.game.order('London move to Belgium via convoy')
        self.game.order('North Sea convoys London to Belgium')
        self.game.order('English Channel supports London move to Bel')
        self.game.order('Belgium supports North Sea hold')
        self.game.order('Heligoland Bight supports SKA move to NTH')
        self.game.order('Skagerrack move to North Sea')
        self.game.adjudicate()
        self.assertIn('English Army in London move via convoy to Belgium '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Skagerrack move to North Sea (fails).',
                      self.game.order_archive.loc(0))

    def test_6_F_19(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Tyrrhenian Sea')
        self.game.add_unit('Fleet', 'France', 'Ionian Sea')
        self.game.add_unit('Army', 'France', 'Tunis')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Rome')
        self.game.order('Tunis move to Naples via convoy')
        self.game.order('Tyrrhenian Sea convoys Tunis to Naples')
        self.game.order('Ionian Sea convoys Tunis to Naples')
        self.game.order('Rome move to Tyrrhenian Sea')
        self.game.order('Naples supports Rome move to Tyrrhenian Sea')
        self.game.adjudicate()
        self.assertIn('Italian Fleet in Naples supports the move Rome '
                      'to Tyrrhenian Sea (fails).', self.game.order_archive.loc(0))
        self.assertIn('Italian Fleet in Rome move to Tyrrhenian Sea (fails).',
                      self.game.order_archive.loc(0))

    def test_6_F_20(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Tyrrhenian Sea')
        self.game.add_unit('Army', 'France', 'Tunis')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Ionian Sea')
        self.game.delete_unit('Ankara')
        self.game.delete_unit('Constantinople')
        self.game.delete_unit('Smyrna')
        self.game.add_unit('Fleet', 'Turkey', 'Eastern Mediterranean')
        self.game.add_unit('Fleet', 'Turkey', 'Aegean Sea')
        self.game.order('Tunis move to Naples via convoy')
        self.game.order('Tyrrhenian Sea convoys Tunis to Naples')
        self.game.order('Ionian Sea convoys Tunis to Naples')
        self.game.order('Aegean Sea supports EMS move to Ionian Sea')
        self.game.order('Naples supports Ionian Sea holds')
        self.game.order('Eastern Mediterranean move to Ionian Sea')
        self.game.adjudicate()
        self.assertIn('Italian Fleet in Naples supports the Fleet in Ionian '
                      'Sea holds (fails).', self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Tyrrhenian Sea convoys Tunis to Naples '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('Turkish Fleet in Eastern Mediterranean move to Ionian '
                      'Sea (succeeds).', self.game.order_archive.loc(0))

    def test_6_F_21(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Irish Sea')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Atlantic Ocean')
        self.game.add_unit('Fleet', 'England', 'Clyde')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Edinburgh')
        self.game.add_unit('Army', 'Russia', 'Norway')
        self.game.add_unit('Fleet', 'Russia', 'Norwegian Sea')
        self.game.order('Norway move to Clyde via convoy')
        self.game.order('Norwegian Sea convoys Norway to Clyde')
        self.game.order('Edinburgh supports Norway move to clyde')
        self.game.order('Mid-Atlantic Ocean move to NAO')
        self.game.order('Irish Sea supports MAO move to NAO')
        self.game.order('Liverpool move to Clyde via convoy')
        self.game.order('North Atlantic Ocean convoy Liverpool to Clyde')
        self.game.order('Clyde supports North Atlantic Ocean holds')
        self.game.adjudicate()
        self.assertIn('French Fleet in Mid-Atlantic Ocean move to North '
                      'Atlantic Ocean (succeeds).', self.game.order_archive.loc(0))

    def test_6_F_22(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Belgium')
        self.game.add_unit('Fleet', 'Germany', 'Picardy')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Norway')
        self.game.add_unit('Fleet', 'Russia', 'North Sea')
        self.game.delete_unit('Ankara')
        self.game.delete_unit('Constantinople')
        self.game.delete_unit('Smyrna')
        self.game.order('Edinburgh move to North Sea')
        self.game.order('London supports Edinburgh move to North Sea')
        self.game.order('Brest move to London via Convoy')
        self.game.order('English Channel convoys Brest to London')
        self.game.order('Picardy move to English Channel')
        self.game.order('Belgium supports Picardy move to ENG')
        self.game.order('Norway move to Belgium')
        self.game.order('North Sea convoys Norway to Belgium')
        self.game.adjudicate()
        self.assertIn('English Fleet in Edinburgh move to North Sea '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Brest move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('German Fleet in Picardy move to English Channel '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in North Sea convoys Norway to Belgium '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_F_23(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Belgium')
        self.game.add_unit('Fleet', 'Germany', 'London')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Irish Sea')
        self.game.add_unit('Fleet', 'Italy', 'Mid-Atlantic Ocean')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Norway')
        self.game.add_unit('Fleet', 'Russia', 'North Sea')
        self.game.order('Edinburgh move to North Sea')
        self.game.order('Yorkshire supports Edinburgh move to North Sea')
        self.game.order('Brest move to London via convoy')
        self.game.order('English Channel convoys Brest to London')
        self.game.order('London supports North Sea Hold')
        self.game.order('Belgium supports English Channel holds')
        self.game.order('Mid-Atlantic Ocean move to English Channel')
        self.game.order('Irish Sea supports MAO move to ENG')
        self.game.order('Norway move to Belgium via convoy')
        self.game.order('North Sea convoys Norway to Belgium')
        self.game.adjudicate()
        self.assertIn('English Fleet in Edinburgh move to North Sea '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Brest move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Italian Fleet in Mid-Atlantic Ocean move to English '
                      'Channel (fails).', self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Norway move via convoy to Belgium '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_F_24(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Belgium')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.add_unit('Fleet', 'England', 'Irish Sea')
        self.game.add_unit('Fleet', 'England', 'Mid-Atlantic Ocean')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Norway')
        self.game.add_unit('Fleet', 'Russia', 'North Sea')
        self.game.order('Edinburgh move to North Sea')
        self.game.order('London supports Edinburgh move to North Sea')
        self.game.order('Irish Sea move to English Channel')
        self.game.order('MAO  supports Irish Sea move to ENG')
        self.game.order('Brest move to London via convoy')
        self.game.order('English Channel convoys Brest to London')
        self.game.order('Belgium supports English Channel holds')
        self.game.order('Norway move to Belgium via convoy')
        self.game.order('North Sea convoys Norway to Belgium')
        self.game.adjudicate()
        self.assertIn('English Fleet in Irish Sea move to English Channel '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('English Fleet in Edinburgh move to North Sea '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Brest move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Norway move via convoy to Belgium '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_G_1(self):
        self.game.add_unit('Fleet', 'England', 'Skagerrack')
        self.game.add_unit('Army', 'England', 'Norway')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Sweden')
        self.game.order('Norway move to Sweden via Convoy')
        self.game.order('Skagerrack convoys Norway to Sweden')
        self.game.order('Sweden move to Norway')
        self.game.adjudicate()
        self.assertIn('English Army in Norway move via convoy to Sweden '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Sweden move to Norway (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_G_2(self):
        self.game.add_unit('Fleet', 'England', 'Skagerrack')
        self.game.add_unit('Army', 'England', 'Norway')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Sweden')
        self.game.order('Norway move to Sweden')
        self.game.order('Skagerrack convoys Norway to Sweden')
        self.game.order('Sweden move to Norway')
        self.game.adjudicate()
        self.assertIn('English Army in Norway move to Sweden (fails).', 
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Sweden move to Norway (fails).', 
                      self.game.order_archive.loc(0))

    def test_6_G_3(self):
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Army', 'France', 'Picardy')
        self.game.add_unit('Army', 'France', 'Burgundy')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.order('Brest move to English Channel')
        self.game.order('Picardy move to Belgium')
        self.game.order('Burgundy supports picardy move to Belgium')
        self.game.order('Mid-Atlantic Ocean supports Brest move to ENG')
        self.game.order('English Channel convoy Picardy to Belgium')
        self.game.adjudicate()
        self.assertIn('French Army in Picardy move to Belgium (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_G_4(self):
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Army', 'France', 'Picardy')
        self.game.add_unit('Army', 'France', 'Burgundy')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Army', 'England', 'Belgium')
        self.game.order('Brest move to English Channel')
        self.game.order('Picardy move to Belgium')
        self.game.order('Burgundy supports picardy move to Belgium')
        self.game.order('Mid-Atlantic Ocean supports Brest move to ENG')
        self.game.order('English Channel convoy Picardy to Belgium')
        self.game.order('Belgium move to Picardy')
        self.game.adjudicate()
        self.assertIn('French Army in Picardy move to Belgium (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_G_5(self):
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Tyrrhenian Sea')
        self.game.add_unit('Army', 'Italy', 'Rome')
        self.game.delete_unit('Ankara')
        self.game.delete_unit('Constantinople')
        self.game.delete_unit('Smyrna')
        self.game.add_unit('Fleet', 'Turkey', 'Ionian Sea')
        self.game.add_unit('Army', 'Turkey', 'Apulia')
        self.game.order('Rome move to Apulia')
        self.game.order('Tyrrhenian Sea convoy Apulia to Rome')
        self.game.order('Apulia move to Rome via convoy')
        self.game.order('Ionian Sea convoy Apulia to Rome')
        self.game.adjudicate()
        self.assertIn('Italian Army in Rome move to Apulia (succeeds).',
                      self.game.order_archive.loc(0))
        self.assertIn('Turkish Army in Apulia move via convoy to Rome '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_G_6(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Irish Sea')
        self.game.add_unit('Fleet', 'France', 'North Sea')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Army', 'England', 'Liverpool')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Edinburgh')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Fleet', 'Russia', 'Norwegian Sea')
        self.game.add_unit('Fleet', 'Russia', 'North Atlantic Ocean')
        self.game.order('Liverpool move to Edinburgh via convoy')
        self.game.order('English Channel convoys Liverpool to Edinburgh')
        self.game.order('Edinburgh move to Liverpool')
        self.game.order('Irish Sea Holds')
        self.game.order('North Sea Holds')
        self.game.order('Norwegian Sea convoy Liverpool to Edinburgh')
        self.game.order('North Atlantic Ocean convoy Liverpool to Edi')
        self.game.adjudicate()
        self.assertIn('English Army in Liverpool move via convoy to Edinburgh '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('German Army in Edinburgh move to Liverpool (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_G_7(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Norway')
        self.game.add_unit('Fleet', 'England', 'Skagerrack')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Sweden')
        self.game.add_unit('Fleet', 'Russia', 'Gulf of Bothnia')
        self.game.order('Norway move to Sweden')
        self.game.order('Skagerrack convoys Sweden move to Norway')
        self.game.order('Sweden move to Norway via convoy')
        self.game.order('Gulf of Bothnia convoy Sweden move to Norway')
        self.game.adjudicate()
        self.assertIn('English Fleet in Norway move to Sweden (succeeds).',
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Sweden move via convoy to Norway '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_G_8(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Army', 'France', 'Belgium')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.delete_unit('Kiel')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army', 'England', 'Holland')
        self.game.order('Belgium move to Holland via Convoy')
        self.game.order('North Sea move to Heligoland Bight')
        self.game.order('Holland move to Kiel')
        self.game.adjudicate()
        # Explicit convoying
        # self.assertIn('French Army in Belgium move via convoy to Holland '
        #               '(fails).', self.game.order_archive.loc(0))
        # webDip rule adjustment
        self.assertIn('French Army in Belgium move to Holland (succeeds).',
                      self.game.order_archive.loc(0))

    def test_6_G_10(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'North Sea')
        self.game.add_unit('Fleet', 'France', 'Norwegian Sea')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Denmark')
        self.game.add_unit('Army', 'England', 'Norway')
        self.game.add_unit('Army', 'England', 'Finland')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Skagerrack')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Sweden')
        self.game.add_unit('Fleet', 'Russia', 'Barents Sea')
        self.game.order('Norway - Sweden via convoy')
        self.game.order('Denmark S Norway - Sweden')
        self.game.order('Finland S Norway - Sweden')
        self.game.order('Skagerrack convoys Norway move to  Sweden')
        self.game.order('Sweden - Norway')
        self.game.order('Barents Sea S Sweden - Norway')
        self.game.order('Norwegian Sea - Norway')
        self.game.order('North Sea S Norwegian Sea - Norway')
        self.game.adjudicate()
        self.assertIn('French Fleet in Norwegian Sea move to Norway (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Sweden move to Norway (fails).',
                      self.game.order_archive.loc(0))

    def test_6_G_11(self):
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Fleet', 'England', 'Norway')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Sweden')
        self.game.add_unit('Fleet', 'Russia', 'Barents Sea')
        self.game.add_unit('Fleet', 'Russia', 'Skagerrack')
        self.game.order('Norway S North Sea - Skagerrack')
        self.game.order('North Sea - Skagerrack')
        self.game.order('Sweden - Norway via convoy')
        self.game.order('Barents Sea S Sweden - Norway')
        self.game.order('Skagerrack C Sweden - Norway')
        self.game.adjudicate()
        self.assertIn('Russian Army in Sweden move via convoy to Norway '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('Russian Fleet in Skagerrack convoys Sweden to Norway '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_G_12(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Atlantic Ocean')
        self.game.add_unit('Fleet', 'England', 'Norwegian Sea')
        self.game.add_unit('Army',  'England', 'Liverpool')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army',  'Germany', 'Edinburgh')
        self.game.add_unit('Fleet', 'Germany', 'North Sea')
        self.game.add_unit('Fleet', 'Germany', 'English Channel')
        self.game.add_unit('Fleet', 'Germany', 'Irish Sea')
        self.game.order('Liverpool move to Edinburgh via convoy')
        self.game.order('North Atlantic Ocean convoy Liverpool to Edi')
        self.game.order('Norwegian Sea convoy Liverpool to Edinburgh')
        self.game.order('Edinburgh move to Liverpool via convoy')
        self.game.order('North Sea convoy Edinburgh move to Liverpool')
        self.game.order('English Channel convoy Edinburgh move to Lvp')
        self.game.order('Irish Sea convoy Edinburgh move to Liverpool')
        self.game.adjudicate()
        self.assertIn('English Army in Liverpool move via convoy to Edinburgh '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('German Army in Edinburgh move via convoy to Liverpool '
                      '(succeeds).', self.game.order_archive.loc(0))

    def test_6_G_13(self):
        self.game.delete_unit('Trieste')
        self.game.delete_unit('Vienna')
        self.game.delete_unit('Budapest')
        self.game.add_unit('Fleet', 'Austria', 'Adriatic Sea')
        self.game.add_unit('Army',  'Austria', 'Trieste')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Albania')
        self.game.add_unit('Army',  'Italy', 'Venice')
        self.game.order('Trieste move to Venice via convoy')
        self.game.order('Adriatic Sea convoy Trieste to Venice')
        self.game.order('Albania move to Trieste')
        self.game.order('Venice supports Albania move to Trieste')
        self.game.adjudicate()
        self.assertIn('Italian Army in Venice supports the move Albania '
                      'to Trieste (succeeds).', self.game.order_archive.loc(0))

    def test_6_G_14(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Norwegian Sea')
        self.game.add_unit('Fleet', 'France', 'North Sea')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Finland')
        self.game.add_unit('Fleet', 'England', 'Denmark')
        self.game.add_unit('Army',  'England', 'Norway')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Germany', 'Skagerrack')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Sweden')
        self.game.add_unit('Fleet', 'Russia', 'Barents Sea')
        self.game.order('Norway move to Sweden')
        self.game.order('Denmark supports Norway move to Sweden')
        self.game.order('Finland supports Norway move to Sweden')
        self.game.order('Norwegian Sea move to Norway')
        self.game.order('North Sea supports Norwegian Sea move to Nwy')
        self.game.order('Skagerrack convoy Sweden to Norway')
        self.game.order('Sweden move to Norway via convoy')
        self.game.order('Barents Sea supports Sweden move to Norway')                 
        self.game.adjudicate()
        self.assertIn('English Army in Norway move to Sweden (succeeds).',
                      self.game.order_archive.loc(0))
        self.assertIn('French Fleet in Norwegian Sea move to Norway (fails).',
                      self.game.order_archive.loc(0))
        self.assertIn('Russian Army in Sweden move via convoy to Norway '
                      '(fails).', self.game.order_archive.loc(0))

    def test_6_G_15(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army',  'France', 'Belgium')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army',  'England', 'Holland')
        self.game.add_unit('Army',  'England', 'Yorkshire')
        self.game.add_unit('Army',  'England', 'London')
        self.game.order('Yorkshire move to London')
        self.game.order('North Sea convoy London to Belgium')
        self.game.order('Holland supports London move to Belgium')
        self.game.order('London move to Belgium via convoy')
        self.game.order('English Channel convoy Belgium to London')
        self.game.order('Belgium move to London via convoy')       
        self.game.adjudicate()
        self.assertIn('English Fleet in North Sea convoys London to Belgium '
                      '(succeeds).', self.game.order_archive.loc(0))
        self.assertIn('French Army in Belgium move via convoy to London '
                      '(fails).', self.game.order_archive.loc(0))
        self.assertIn('English Army in Yorkshire move to London (fails).',
                      self.game.order_archive.loc(0))

    def test_6_G_16(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Baltic Sea')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army',  'England', 'Norway')
        self.game.add_unit('Army',  'England', 'Denmark')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army',  'Russia', 'Sweden')
        self.game.add_unit('Fleet', 'Russia', 'Norwegian Sea')
        self.game.add_unit('Fleet', 'Russia', 'Skagerrack')
        self.game.order('Norway move to Sweden')
        self.game.order('Denmark supports Norway move to Sweden')
        self.game.order('Baltic Sea supports Norway move to Sweden')
        self.game.order('North Sea move to Norway')
        self.game.order('Sweden move to Norway via convoy')
        self.game.order('Skagerrack convoy Sweden move to Norway')
        self.game.order('Norwegian Sea supports Sweden move to Norway')       
        self.game.adjudicate()
        self.assertIn('English Fleet in North Sea move to Norway (fails).',
                      self.game.order_archive.loc(0))
        
    def test_6_G_17(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Baltic Sea')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Fleet', 'England', 'Skagerrack')
        self.game.add_unit('Army',  'England', 'Norway')
        self.game.add_unit('Army',  'England', 'Denmark')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army',  'Russia', 'Sweden')
        self.game.add_unit('Fleet', 'Russia', 'Norwegian Sea')
        self.game.order('Norway move to Sweden via convoy')
        self.game.order('Denmark supports Norway move to Sweden')
        self.game.order('Baltic Sea supports Norway move to Sweden')
        self.game.order('North Sea move to Norway')
        self.game.order('Sweden move to Norway')
        self.game.order('Skagerrack convoy Norway move to Sweden')
        self.game.order('Norwegian Sea supports Sweden move to Norway')       
        self.game.adjudicate()
        self.assertIn('English Fleet in North Sea move to Norway (fails).',
                      self.game.order_archive.loc(0))

    def test_6_G_18(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'English Channel')
        self.game.add_unit('Army',  'France', 'Belgium')
        self.game.add_unit('Army',  'France', 'Wales')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army',  'England', 'Holland')
        self.game.add_unit('Army',  'England', 'Yorkshire')
        self.game.add_unit('Army',  'England', 'London')
        self.game.add_unit('Army',  'England', 'Ruhr')
        self.game.order('London move to Belgium via convoy')
        self.game.order('Yorkshire move to London')
        self.game.order('North Sea convoys London to Belgium')
        self.game.order('Holland supports London move to Belgium')
        self.game.order('Ruhr supports London move to Belgium')
        self.game.order('Belgium move to London via convoy')
        self.game.order('Wales supports Belgium move to London')
        self.game.order('English Channel convoys Belgium to London')       
        self.game.adjudicate()
        self.assertIn('English Army in Yorkshire move to London (fails).',
                      self.game.order_archive.loc(0))

    def test_6_H_5(self):
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Fleet', 'Russia', 'Black Sea')
        self.game.delete_unit('Ankara')
        self.game.delete_unit('Constantinople')
        self.game.delete_unit('Smyrna')
        self.game.add_unit('Fleet', 'Turkey', 'Ankara')
        self.game.add_unit('Fleet', 'Turkey', 'Constantinople')
        self.game.order('Ankara move to Black Sea')
        self.game.order('Constantinople supports Ankara move to BLA')
        self.game.order('Black Sea Holds')       
        self.game.adjudicate()
        self.game.order('Black Sea retreats to Ankara')   
        self.game.adjudicate()
        self.assertIn('The Fleet in Black Sea retreats to Ankara (fails).', 
                      self.game.order_archive.loc(1))

    def test_6_H_6(self):
        self.game.delete_unit('Trieste')
        self.game.delete_unit('Vienna')
        self.game.delete_unit('Budapest')
        self.game.add_unit('Army',  'Austria', 'Trieste')
        self.game.add_unit('Army',  'Austria', 'Budapest')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Munich')
        self.game.add_unit('Army', 'Germany', 'Silesia')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Army',  'Italy', 'Vienna')
        self.game.order('Trieste move to Vienna')
        self.game.order('Budapest supports Trieste move to Vienna')
        self.game.order('Munich move to Bohemia')       
        self.game.order('Silesia move to Bohemia')
        self.game.order('Vienna holds')    
        self.game.adjudicate()
        self.game.order('Vienna retreats to Bohemia')
        self.game.adjudicate()
        self.assertIn('The Army in Vienna retreats to Bohemia (fails).', 
                      self.game.order_archive.loc(1))

    def test_6_H_7(self):
        self.game.delete_unit('Trieste')
        self.game.delete_unit('Vienna')
        self.game.delete_unit('Budapest')
        self.game.add_unit('Army',  'Austria', 'Trieste')
        self.game.add_unit('Army',  'Austria', 'Budapest')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Munich')
        self.game.add_unit('Army', 'Germany', 'Silesia')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Army',  'Italy', 'Vienna')
        self.game.add_unit('Army',  'Italy', 'Bohemia')
        self.game.order('Trieste move to Vienna')
        self.game.order('Budapest supports Trieste move to Vienna')
        self.game.order('Munich supports Silesia move to Bohemia')       
        self.game.order('Silesia move to Bohemia')
        self.game.order('Vienna holds')    
        self.game.order('Bohemia holds')   
        self.game.adjudicate()
        self.game.order('Vienna retreats to Tyrolia')
        self.game.order('Bohemia retreats to Tyrolia')
        self.game.adjudicate()
        self.assertIn('The Army in Vienna retreats to Tyrolia (fails).', 
                      self.game.order_archive.loc(1))
        self.assertIn('The Army in Bohemia retreats to Tyrolia (fails).', 
                      self.game.order_archive.loc(1))

    def test_6_H_8(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Yorkshire')
        self.game.add_unit('Fleet', 'England', 'Norway')
        self.game.add_unit('Army',  'England', 'Liverpool')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Kiel')
        self.game.add_unit('Army', 'Germany', 'Ruhr')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Sweden')
        self.game.add_unit('Army',  'Russia', 'Finland')
        self.game.add_unit('Fleet', 'Russia', 'Edinburgh')
        self.game.add_unit('Fleet', 'Russia', 'Holland')
        self.game.order('Liverpool move to Edinburgh')
        self.game.order('Yorkshire supports Liverpool move to Edi')
        self.game.order('Norway holds')       
        self.game.order('Kiel supports Ruhr move to Holland')
        self.game.order('Ruhr move to Holland')    
        self.game.order('Edinburgh holds')
        self.game.order('Sweden supports Finland move to Norway')
        self.game.order('Finland move to Norway')
        self.game.order('Holland holds')   
        self.game.adjudicate()
        self.game.order('Norway retreats to North Sea')
        self.game.order('Edinburgh retreats to North Sea')
        self.game.order('Holland move to North Sea')
        self.game.adjudicate()
        self.assertIn('The Fleet in Norway retreats to North Sea (fails).',
                      self.game.order_archive.loc(1))
        self.assertIn('The Fleet in Edinburgh retreats to North Sea (fails).', 
                      self.game.order_archive.loc(1))
        self.assertIn('The Fleet in Holland retreats to North Sea (fails).', 
                      self.game.order_archive.loc(1))

    def test_6_H_9(self):
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Heligoland Bight')
        self.game.add_unit('Fleet', 'England', 'Denmark')
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Berlin')
        self.game.add_unit('Army', 'Germany', 'Silesia')
        self.game.add_unit('Fleet', 'Germany', 'Kiel')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Prussia')
        self.game.order('Heligoland Bight move to Kiel')
        self.game.order('Denmark supports Heligoland Bight move to Kiel')
        self.game.order('Berlin move to Prussia')
        self.game.order('Kiel holds')
        self.game.order('Silesia supports Berlin move to Prussia')
        self.game.order('Prussia move to Berlin')
        self.game.adjudicate()
        self.game.order('Kiel retreats to Berlin')
        self.game.adjudicate()
        self.assertIn('The Fleet in Kiel retreats to Berlin.', 
                      self.game.order_archive.loc(1))

    def test_6_H_10(self):
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Kiel')
        self.game.delete_unit('Munich')
        self.game.add_unit('Army', 'Germany', 'Berlin')
        self.game.add_unit('Army', 'Germany', 'Prussia')
        self.game.add_unit('Army', 'Germany', 'Munich')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Army',  'Italy', 'Kiel')
        self.game.delete_unit('Moscow')
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Silesia')
        self.game.add_unit('Army', 'Russia', 'Warsaw')
        self.game.order('Kiel holds')
        self.game.order('Berlin move to Kiel')
        self.game.order('Munich supports Berlin move to Kiel')
        self.game.order('Warsaw move to Prussia')
        self.game.order('Silesia supports Warsaw move to Prussia')
        self.game.adjudicate()
        self.game.order('Kiel retreats to Berlin')
        self.game.order('Prussia retreats to Berlin')
        self.game.adjudicate()
        self.assertIn('The Army in Prussia retreats to Berlin.', 
                      self.game.order_archive.loc(1))
        self.assertIn('The Army in Kiel retreats to Berlin (fails).',
                      self.game.order_archive.loc(1))

    def test_6_H_11(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'France', 'Western Mediterranean')
        self.game.add_unit('Fleet', 'France', 'Gulf of Lyon')
        self.game.add_unit('Army',  'France', 'Gascony')
        self.game.add_unit('Army',  'France', 'Burgundy')
        self.game.delete_unit('Naples')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Army',  'Italy', 'Marseilles')
        self.game.order('Gascony move to Marseilles via convoy')
        self.game.order('Mid-Atlantic Ocean convoy Gascony to Mar')
        self.game.order('Western Mediterranean convoys Gascony to Mar')
        self.game.order('Gulf of Lyon convoys Gascony to Marseilles')
        self.game.order('Burgundy supports Gascony move to Marseilles')
        self.game.adjudicate()
        self.game.order('Marseilles retreats to Gascony')
        self.game.adjudicate()
        self.assertIn('The Army in Marseilles retreats to Gascony.', 
                      self.game.order_archive.loc(1))

    def test_6_H_12(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'France', 'Brest')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Irish Sea')
        self.game.add_unit('Fleet', 'England', 'English Channel')
        self.game.add_unit('Fleet', 'England', 'North Sea')
        self.game.add_unit('Army',  'England', 'Liverpool')
        self.game.delete_unit('Saint Petersburg')
        self.game.delete_unit('Sevastopol')
        self.game.add_unit('Army', 'Russia', 'Edinburgh')
        self.game.add_unit('Army', 'Russia', 'Clyde')
        self.game.add_unit('Fleet', 'Russia', 'Norwegian Sea')
        self.game.add_unit('Fleet', 'Russia', 'North Atlantic Ocean')
        self.game.order('Liverpool move to Edinburgh via convoy')
        self.game.order('Irish Sea convoy Liverpool to Edinburgh')
        self.game.order('English Channel convoy Liverpool to Edinburgh')
        self.game.order('North Sea convoy Liverpool to Edinburgh')
        self.game.order('Brest move to English Channel')
        self.game.order('Mid-Atlantic Ocean supports Brest move to ENG')
        self.game.order('Edinburgh move to Liverpool via convoy')
        self.game.order('Norwegian Sea convoy Edinburgh to Liverpool')
        self.game.order('North Atlantic Ocean convoy Edi move to Lvp')
        self.game.order('Clyde supports Edinburgh move to Liverpool')    
        self.game.adjudicate()
        self.game.order('Liverpool retreats to Edinburgh')
        self.game.adjudicate()
        self.assertIn('The Army in Liverpool retreats to Edinburgh.',
                      self.game.order_archive.loc(1))

    def test_6_H_15(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'France', 'Spain (south coast)')
        self.game.delete_unit('Liverpool')
        self.game.delete_unit('London')
        self.game.delete_unit('Edinburgh')
        self.game.add_unit('Fleet', 'England', 'Portugal')
        self.game.order('Portugal holds')
        self.game.order('Spain move to Portugal')
        self.game.order('Mid-Atlantic Ocean supports Spain move to Por')                 
        self.game.adjudicate()
        self.game.order('Portugal retreats to Spain (north coast)')
        self.game.adjudicate()
        self.assertIn(('The Fleet in Portugal retreats to Spain (north coast)'
                       ' (fails).'), self.game.order_archive.loc(1))

    def test_6_H_16(self):
        self.game.delete_unit('Brest')
        self.game.delete_unit('Paris')
        self.game.delete_unit('Marseilles')
        self.game.add_unit('Fleet', 'France', 'Mid-Atlantic Ocean')
        self.game.add_unit('Fleet', 'France', 'Gascony')
        self.game.add_unit('Fleet', 'France', 'Western Mediterranean')
        self.game.delete_unit('Rome')
        self.game.delete_unit('Venice')
        self.game.add_unit('Fleet', 'Italy', 'Tyrrhenian Sea')
        self.game.add_unit('Fleet', 'Italy', 'Tunis')
        self.game.order('Gascony move to Spain (north coast)')
        self.game.order('Western Mediterranean holds')
        self.game.order('Mid-Atlantic Ocean move to Spain (north coast)')
        self.game.order('Tunis supports Tyrrhenian Sea move to WMS')
        self.game.order('Tyrrhenian Sea move to Western Mediterranean')
        self.game.adjudicate()
        self.game.order('WMS retreats to Spain (south coast)')
        self.game.adjudicate()
        self.assertIn(('The Fleet in Western Mediterranean retreats to Spain '
                       '(south coast) (fails).'), self.game.order_archive.loc(1))

    def test_6_I_2(self):
        with self.assertRaises(ValueError):
            self.game.delete_unit('Moscow')
            self.game.delete_unit('Warsaw')
            self.game.adjudicate()
            self.game.adjudicate()
            self.game.order('Russia 1 build Fleet Moscow')
            self.game.adjudicate()
            self.assertIn('The Fleet in Western Mediterranean disbands.',
                          self.game.order_archive.loc(1))

    def test_6_I_3(self):
        self.game.delete_unit('Moscow')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.order('Russia 1 build Army StP (north coast)')
        self.game.adjudicate()
        self.assertEqual(len(self.game.units), 21)

    def test_6_I_4(self):
        self.game.delete_unit('Moscow')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.order('Russia 1 build Fleet Saint Petersburg (n)')
        self.game.adjudicate()
        self.assertEqual(len(self.game.units), 21)

    def test_6_I_5(self):
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Munich')
        self.game.add_unit('Fleet', 'Russia', 'Baltic Sea')
        self.game.add_unit('Army', 'Russia', 'Berlin')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.order('Russia 1 disband Berlin')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.adjudicate()  
        self.game.order('Germany 1 Build Army Berlin')
        self.game.adjudicate()
        self.assertEqual(len(self.game.units), 21)
        
    def test_6_I_6(self):
        self.game.delete_unit('Berlin')
        self.game.delete_unit('Sevastopol')
        self.game.delete_unit('Saint Petersburg')
        self.game.add_unit('Army', 'Russia', 'Berlin')
        self.game.add_unit('Fleet', 'Russia', 'Baltic Sea')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.delete_unit('Berlin')
        self.game.adjudicate()  
        self.game.adjudicate()  
        self.game.order('Russia 1 Build Army Berlin')
        self.game.adjudicate()
        self.assertEqual(len(self.game.units), 20)
        
    def test_6_I_7(self):
        self.game.delete_unit('Warsaw')
        self.game.delete_unit('Sevastopol')
        self.game.adjudicate()
        self.game.adjudicate()
        self.game.order('Russia 1 Build Fleet Sevastopol')
        self.game.order('Russia 2 Build Army Sevastopol')
        self.game.adjudicate()
        self.assertEqual(len(self.game.units), 21)

if __name__ == '__main__':
    unittest.main()
        