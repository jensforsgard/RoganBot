""" The function: isorderinstance

"""


from yaml import load, Loader

with open('adjudicator/config.yaml', 'r') as file:
    RELEVANCE = load(file, Loader)['relevance']


def isorderinstance(order, instance):
    """ Tests if an order is of a given instance. Instances are
    encoded by their name as a string, and the identification is
    made be checking the `relevance` attribute, which is stored
    in the config file.
    
    """
    return order.relevance == RELEVANCE[instance.lower()]
