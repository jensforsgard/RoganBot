""" The Province class

"""

class Province:
    """ A Province is an area on the map.  

    Parameters / Attributes
    -----------------------
    idn : integer
        The id number of the province
    
    name : string
        The name of the province.
        
    short : string
        The three letter abbreviation of the province.
        
    supply_center : bool
        Whether the province is a supply center or not.

    Notes
    -----
    There is no consistency checks on paramaters.

    See also the Location class in ._location. A Location is a
    contained attached to a Province, which may contain a unit
    of a specified Force instance. The Location class also stores
    information about adjacencies (since adjacencies depend on
    the Force instance.)

    """

    def __init__(self, idn, **kwargs):
        """ Constructor.

        """
        self.idn = int(idn)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        """ Print format.

        """
        return self.name
