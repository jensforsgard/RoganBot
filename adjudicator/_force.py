class Force:
    """ A Force is a type of unit.
    
    Attributes:
        name: string
        may_receive: list of strings
            List of orders, as strings, which the force may be object of.
        specifiers: list of strings
            List of specifiers of locations that can contain the force.
        short_forms: dictionary
            Short forms of the specifiers.

    """



    def __init__(self, name, dctnry):
        """ Constructor.

        """
        self.name = name
        self.may_receive = tuple(dctnry['may receive'])
        self.specifiers = tuple(dctnry['specifiers'])
        self.short_forms = dict(zip(dctnry['short forms'], self.specifiers))



    def __str__(self):
        """ Print format.

        """
        return self.name