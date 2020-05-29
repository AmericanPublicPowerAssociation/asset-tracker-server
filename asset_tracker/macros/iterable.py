from itertools import tee


class PairSet(set):

    def add(self, pair):
        super().add(get_sorted_tuple(pair))

    def update(self, pairs):
        super().update(get_sorted_tuple(_) for _ in pairs)

    def union(self, pairs):
        return super().union(get_sorted_tuple(_) for _ in pairs)


def get_adjacent_pairs(iterable):
    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    a, b = tee(iterable)  # Make two independent iterators
    next(b, None)  # Advance second iterator
    return zip(a, b)  # Zip!


def get_sorted_tuple(iterable):
    return tuple(sorted(iterable))
