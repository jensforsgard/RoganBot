""" The OrderStatus class

"""


class OrderStatus:
    """ An instance is the min/max status of an order.
    
    Parameters
    ----------
    status : string
        The status at instantiation.
    
    Attributes
    ----------
    status : string
        See Parameters.
    
    statuses : dictionary
        Keys are possible statuses, and values are their numerical
        values (which determine the ordering).
    
    The main purpose of this class is to allow orders statuses to be
    strings, while still comparing them.

    """

    statuses = {
        'valid': 4,
        'no effect': 3,
        'cut': 2,
        'broken': 1,
        'illegal': 0
    }

    def __init__(self, status):
        """ Constructor.
 
        """
        self.set(status)

    def __str__(self):
        """ Print format.
        
        """
        return self.status

    def set(self, value):
        """ Sets the status to the entered value.
        
        """
        assert value in self.statuses

        self.status = value        

    @property
    def value(self):
        """ Returns the numerical value of the status.
        
        """
        return self.statuses[self.status]

    def __lt__(self, other):
        """ Less than operator.
        
        """
        try:
            return self.value < other.value
        
        except AttributeError:
            return self.value < self.statuses[other]

    def __gt__(self, other):
        """ Greater than operator.
        
        """
        try:
            return self.value > other.value
        
        except AttributeError:
            return self.value > self.statuses[other]

    def __eq__(self, other):
        """ Equal to operator.
        
        """
        try:
            return self.value == other.value

        except AttributeError:
            return self.value == self.statuses[other]
