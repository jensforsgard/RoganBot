""" Unittests for the Force class.

The tests should be run from the base directory.

"""

import unittest

from adjudicator import Force

class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.force = Force(
            name='Army',
            may_receive=['Hold'],
            specifiers=['A', 'B'],
            short=['a', 'b']
        )

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test__init__(self):
        self.assertEqual(
            self.force.name,
            'Army'
        )
        self.assertEqual(
            self.force.may_receive,
            tuple(['Hold'])
        )
        self.assertEqual(
            self.force.specifiers,
            ('A', 'B')
        )
        self.assertEqual(
            self.force.short_forms,
            {'a': 'A', 'b': 'B'}
        )

    def test__str__(self):
        self.assertEqual(
            self.force.__str__(),
            'Army'
        )

if __name__ == '__main__':
    unittest.main()
