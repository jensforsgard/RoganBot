""" The Require wrapper

"""

def require(func):
    """ Throws a ValueError if an output is required but not generated.
    That an output is required is signalled by setting the keyword
    `require` being set to True, 

    """
    def wrapper(*args, **kwargs):

        require = False

        if 'require' in kwargs:
            require = kwargs['require']
            del kwargs['require']

        value = func(*args, **kwargs)

        if require and value is None:
            raise ValueError("Output requested but 'None' obtained.")

        return value

    return wrapper
