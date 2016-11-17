# -*- coding: utf-8 -*-

import itertools
import operator

from . core import Base, Pipe, Origin


class Limit(Pipe):
    def __init__(self, limit):
        super(Limit, self).__init__()
        self.limit = limit

    def _initialize(self):
        count = 0
        for x in self.upstream:
            if count >= self.limit:
                raise StopIteration()
            yield x
            count += 1


class Skip(Pipe):
    def __init__(self, skip):
        super(Skip, self).__init__()
        self.skip = skip

    def _initialize(self):
        count = 0
        while count < self.skip:
            next(self.upstream)
            count += 1
        yield from self.upstream


class Chain(Pipe):
    def __init__(self, *iterables):
        super(Chain, self).__init__()
        self.iterables = tuple(it if isinstance(it, Base) else Origin(it)
                               for it in iterables)

    def _initialize(self):
        if self.upstream is not None:
            yield from self.upstream
        for it in self.iterables:
            yield from it


class Enumerate(Pipe):
    def __init__(self):
        super(Enumerate, self).__init__()

    def _initialize(self):
        count = 0
        for x in self.upstream:
            yield (count, x)
            count += 1


class GroupBy(Pipe):
    def __init__(self, keyfunc):
        super(GroupBy, self).__init__()
        self.keyfunc = keyfunc

    def _initialize(self):
        for (k, i) in itertools.groupby(self.upstream, self.keyfunc):
            yield (k, Origin(i))


class Filter(Pipe):
    def __init__(self, filterfunc):
        super(Filter, self).__init__()
        self.filterfunc = filterfunc

    def _initialize(self):
        for x in self.upstream:
            if self.filterfunc(x):
                yield x


class Zip(Pipe):
    def __init__(self, *iterables):
        super(Zip, self).__init__()
        self.iterables = tuple(it if isinstance(it, Base) else Origin(it)
                               for it in iterables)

    def _initialize(self):
        yield from zip(self.upstream, *self.iterables)


class Map(Pipe):
    def __init__(self, func, *iterables):
        super(Map, self).__init__()
        self.func = func
        self.iterables = tuple(it if isinstance(it, Base) else Origin(it)
                               for it in iterables)

    def _initialize(self):
        yield from map(self.func, self.upstream, *self.iterables)


class StarMap(Pipe):
    def __init__(self, func):
        super(StarMap, self).__init__()
        self.func = func

    def _initialize(self):
        yield from itertools.starmap(self.func, self.upstream)


class Accumulate(Pipe):
    def __init__(self, func=None):
        super(Accumulate, self).__init__()
        self.func = func

    def _initialize(self):
        yield from itertools.accumulate(self.upstream,
                                        self.func or operator.add)
