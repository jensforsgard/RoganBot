""" The function: flatten.

"""


def flatten(lists):
    """ Flattens a list of lists on the first level.

    """
    return [item for sublist in lists for item in sublist]
