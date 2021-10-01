""" The BuildOrders class

"""


from adjudicator.orders.lib import OrderCollection


class BuildOrders(OrderCollection):
    """ An instance of BuildOrders is a collection of orders
    for a build phase.

    Parameters
    ----------
    build : Order subclass
        The type of order that should be used for builds
    
    disband : Order subclass
        The type of order that should be used for disbands
    
    scs : dictionary
        A dictionary whose keys are powers and whose values are supply center
        counts
    
    hcs : dictionary
        A dictionary whose keys are powers and whose values are open home
        center counts.
    
    units : dictionary
        A dictionary whose keys are powers and whose values are unit counts.

    """

    def __init__(self, build, disband, scs, hcs, units):
        """ Constructor.
 
        """
        self.orders = []

        for key in scs:
            count = len(scs[key]) - units[key]

            if count > 0:
                count = min(count, hcs[key])
                self.insert([build(j+1, key) for j in range(count)])

            elif count < 0:
                self.insert([disband(j+1, key) for j in range(-count)])
