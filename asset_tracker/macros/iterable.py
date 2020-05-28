from itertools import tee


def get_adjacent_pairs(iterable):
    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    a, b = tee(iterable)  # Make two independent iterators
    next(b, None)  # Advance second iterator
    return zip(a, b)  # Zip!
