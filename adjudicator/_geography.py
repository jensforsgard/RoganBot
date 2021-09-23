""" The Geography class

"""

from adjudicator import Force

class Geography:
    """ A Geography is a container for a unit of a specified force.

    Parameters / Attributes
    -----------------------
        name : string
            The name of the geography.

        map_ : Map
            The game map which the Geography belongs to. 

        force : Force
            Specifying the type of Force that may be contained in an
            instance of Geography.

        orders : list of strings
            The type of orders, encoded by their names, which are available
            for a unit contained in an instance of Geography.

    Notes
    -----
    Names of geographies should be unique, as they are used as the primary
    identifier for a geography.
    
    See also the Location class in ._location. A location is in essense a
    pair consisting of a Province and a Geography; it specifies a location
    on a map where a unit of a specific Force can be located.
    
    The standard map has three geographies: inland, coast, and sea. An inland
    geography can contain `Army` units. A unit contained in an inland geography
    can receive the orders `Hold`, `Move`, and `Support`. Coast and sea 
    geographies can contain `Fleet` units. A unit contained in a coast 
    geography can receive the orders `Hold`, `Move`, and `Support`. A unit 
    ontained in a sea geography can receive the orders `Hold`, `Convoy`, 
    `Move`, and `Support`.

    """

    def __init__(self, name, map_, force, orders):
        """ Constructor.

        """
        self.name = name
        self.map_ = map_
        self.orders = orders

        self.force = map_.instance(force, Force)

    def __str__(self):
        """ Print format.

        """
        return self.name

    def __repr__(self):
        """ Representation.
        
        """
        return (f"Geography(name={self.name}, map={self.map_.name}, "
                f"force={self.force.name}, orders={self.orders})")
