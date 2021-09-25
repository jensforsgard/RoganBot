""" The Variant class

"""

from json import load as json_load

from adjudicator import Map, Power

from lib.classes import make_instances

class Variant:
    """ This is a class of which an instance is variant of
    the game.

    Parameters
    ----------
    name : string
        The name of the variant. Should match the filename of the
        corresponding JSON file in the `variants` folder.

    Attributes
    ----------
    name : string
        The name of the variant.

    loaded : bool
        Whether the information in the JSON file has been loaded
        into the instance or not.

    powers : list of Powers
        A list of the powers appearing in the variant.

    map : Map
        The map the variant is played on.

    starting_year : integer
        The starting year of the variant.

    starting_positions : dictionary
        A dictionary whose keys are the names of the powers in the
        game and whose values are lists of the starting positions of
        the units of the given powers. Each starting position is
        itself given as a dictionary of a force and a location name.

    win_condition : integer
        The number of supply centers needed for a solo win.
    
    unit_colors : dictionary
        A dictionary whose keys are the names of the powers in the
        game ans whose values are colors of units for the graphics
        module.
    
    province_colors : dictionary
        A dictionary whose keys are the names of the powers in the
        game ans whose values are colors of owned supply centers 
        for the graphics module.

    marker_size : integer
        The marker size to be used by the graphics package.
        
    Notes
    -----
    The attributes are loaded when the `load` method is called the
    first time, and not on initialization.

    """

    def __init__(self, name):
        """ Constructor.

        """
        self.name = name
        self.loaded = False

    def __str__(self, suffix='.'):
        """ Print format.

        """
        return self.name

    def load(self):
        """ Loads the variant information from the JSON file with
        the name of the variant.

        """
        with open(f'variants/{self.name}.json') as file:
            data = json_load(file)

        for key, value in data.items():
            setattr(self, key, value)

        self.powers = make_instances(self.powers, Power)
        
        self.map = Map(self.map)
        self.map.load()

        self.loaded = True

    def instance(self, name, class_type):
        """ Returns the instance of a class with a given name.

        Parameters
        ----------
        name : string
            The name of the instance.

        class_type : string or type
            The Class the instance belongs to, or the name
            of the class as a string.

        Notes
        -----
        This method is more general than what it needs to be; on
        the classic map the only class whose instances are stored
        in the `Variant` class are powers.

        """
        classes = {Power: 'powers'}

        try:
            objects = getattr(self, classes[class_type])

        except KeyError:
            objects = getattr(self, class_type)            

        return next((obj for obj in objects if obj.name == name),
                    None)
