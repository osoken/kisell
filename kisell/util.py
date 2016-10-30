# -*- coding; utf-8 -*-

from datetime import datetime
from functools import reduce

from . core import Origin, Pipe


class Attr(Pipe):
    """Just add attributes to this Pipe object.

    :param kwargs: each key word becomes the attribute name and each
    argument becomes the attribute's value
    """
    def __init__(self, **kwargs):
        super(Attr, self).__init__()
        for (k, v) in kwargs:
            setattr(self, k, v)

    def _initialize(self):
        return self.upstream


class Timing(Pipe):
    """Record timestamps when it is ``created_at``, ``initialized_at`` and
    ``finalized_at``.
    """
    def __init__(self):
        super(Timing, self).__init__()
        self.created_at = datetime.now()

    def _initialize(self):
        self.initialized_at = datetime.now()
        return self.upstream

    def _finalize(self):
        self.finalized_at = datetime.now()


class OnInitialize(Pipe):
    """Add initialization hook for this kisell.

    :param f: zero-argument function. this is called when this kisell is
    initialized
    """
    def __init__(self, f):
        super(OnInitialize, self).__init__()
        self.on_initialize = f

    def _initialize(self):
        self.on_initialize()
        return self.upstream


class OnFinalize(Pipe):
    """Add finalization hook for this kisell.

    :param f: zero-argument function. this is called when this kisell is
    finalized.
    """
    def __init__(self, f):
        super(OnFinalize, self).__init__()
        self.on_finalize = f

    def _initialize(self):
        return self.upstream

    def _finalize(self):
        self.on_finalize()


class OnIterate(Pipe):
    """Add iteration hook for this kisell.

    :param f: one-argument function. this is called before each iteration. take
    the item from the upstream as the argument.
    """
    def __init__(self, f):
        super(OnIterate, self).__init__()
        self.on_iterate = f

    def _initialize(self):
        for x in self.upstream:
            self.on_iterate(x)
            yield x


class Count(Pipe):
    """Add counter. ``.count`` attribute indicates how many times the iteration
    occured.
    """
    def __init__(self):
        super(Count, self).__init__()
        self.count = 0

    def _initialize(self):
        for x in self.upstream:
            self.count += 1
            yield x


class CompoOrigin(Origin):
    """Make Origin object consist of origin an

    :param origin: the origin of the kisell component.
    :param args: pipes
    """
    def __init__(self, origin, *args):
        super(CompoOrigin, self).__init__(
            reduce(lambda x, y: x.then(y), args, origin)
        )


class CompoPipe(Pipe):
    """Bundle several pipes.

    :param args: pipes
    """
    def __init__(self, *args):
        super(CompoPipe, self).__init__(reduce(lambda x, y: x.then(y), args))
        self.upstream = self._Pipe__attribute_base

    def _initialize(self):
        return self.upstream
