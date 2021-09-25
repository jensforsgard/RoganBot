""" The Province class

"""

class Power:
    """ A Power is one player in a game.

    Parameters / Attributes
    -----------------------
    name : string
        The name of the power.

    genitive : string
        The genitive form of the name.

    home_centers : list of strings
        The list of home center names of the power,
        recorded as strings.

    """

    def __init__(self, name, genitive, home_centers):
        """ Constructor.

        """
        self.name = name
        self.genitive = genitive
        self.home_centers = home_centers

    def __str__(self, suffix='.'):
        """ Print format.

        """
        return self.name
