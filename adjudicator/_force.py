""" The Force class

"""

class Force:
    """ A Force is a type of unit.

    Parameters
    ----------
        name : string
            The name of the Force.

        may_receive : list of strings
            List of orders, encoded by strings, that the force may receive.

        specifiers : list of strings
            List of specifiers of locations that can contain the force.

        short_forms : list of strings
            List of short forms of the specifiers, assumed to be arranged in
            the same order as the `specifiers` parameter.

    Attributes
    ----------
        name : string
            See Parameters.

        may_receive : list of strings
            See Parameters.

        specifiers : list of strings
            See Parameters.

        short : dictionary
            Dictionary of short forms of the specifiers, where short forms are
            keys and full forms are values.

    Notes
    -----
    Names of forces should be unique, as they are used as the primary
    identifier of a force.

    On the classic map, the Army force has no specifiers, since each province
    has at most one location for an Army. The Fleet force has two specifiers,
    `(south coast)` and `(north coast)`, with short forms `(sc)` and `(nc)`.

    """

    def __init__(self, name, may_receive, specifiers, short):
        """ Constructor.

        """
        self.name = name
        self.may_receive = tuple(may_receive)
        self.specifiers = tuple(specifiers)
        self.short_forms = dict(zip(short, self.specifiers))

    def __str__(self):
        """ Print format.

        """
        return self.name
