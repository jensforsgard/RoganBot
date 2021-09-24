""" The Season class

"""

class Season:
    """ An instance is a ticker which keeps track of the current season
    in a game of Diplomacy.

    Parameters / Attributes
    -----------------------
        name : string
            The name of the current season.
        
        phase : string
            The name of the current phase.
    
        year : integer
            The current year.

        count : integer
            The order of the season.

    Notes
    -----
    The attribute `name` is the name of the current season, and not the
    name of the instance.
    
    A game in 'Pregame' mode will have a year that is one year before
    the starting year of the given variant. This adjusts for that
    the year ticker increases by one each Spring Diplomacy when we
    enter a new Spring Diplomacy phase.

    """

    phases = {
        0: 'Builds',
        1: 'Diplomacy',
        2: 'Retreats',
        3: 'Diplomacy',
        4: 'Retreats'
    }

    names = {
        0: 'Fall',
        1: 'Spring',
        2: 'Spring',
        3: 'Fall',
        4: 'Fall'
    }    

    def __init__(self, year, name='Spring', phase='Pregame', count=0):
        """ Constructor.

        """
        self.name = name
        self.phase = phase
        self.year = year - (phase == 'Pregame')
        self.count = count

    def __str__(self):
        """ Print method.
        
        """
        return f'{self.phase} in {self.name} {str(self.year)}.'

    def reset(self, variant):
        """ Resets the ticker to the pregame status as defined by
        the parameter `variant`, which should be an instance of the
        adjudicator.Variant class.

        """
        self.count = 0
        self.name = 'Spring'
        self.phase = 'Pregame'
        self.year = variant.starting_year - 1

    def __set_name_phase__(self):
        """ Deduces the current season name and phase from the 
        current value of `self.count`.

        """
        k = self.count % 5

        self.phase = self.phases[k]
        self.name = self.names[k]

    def __year_diff__(self, k):
        """ Returns the difference in year that would results from
        shifting the count by k steps.
        
        """
        return ((4 + self.count + k) // 5) - ((4 + self.count) // 5)

    def progress(self, k=1):
        """ Moves the season forward k phases.

        """
        assert self.phase != 'Postgame', (
            'Can not progess a game that is in postgame mode.'
        )

        self.year += self.__year_diff__(k)
        self.count += k

        self.__set_name_phase__()

    def rollback(self, k=1):
        """ Moves the season backwards one phase. 
        
        """
        assert self.count > k, (
            'Cannot rollback to before the first season. '
            'Use the `pregame` method to reset the season ticker.'
        )

        self.year += self.__year_diff__(-k)
        self.count -= k

        self.__set_name_phase__()

    def conclude(self):
        """ Sets the ticker in a postgame mode.
        
        Note: Using the `rollback` method will put the ticker
        back into normal mode.
        
        """
        self.phase = 'Postgame'
        self.count += 1
