# -*- coding: utf-8 -*-

from collections import Iterable
from abc import ABCMeta, abstractmethod
import itertools
import operator


class Error(Exception):
    """Base Exception class of this module
    """
    pass


class EmptyPipeError(Error):
    """This exception is raised when iteration is started without setting the
    origin of the Stream.
    """

    def __init__(self):
        super(EmptyPipeError, self).__init__()


class OriginWithUpstreamError(Error):
    """Exception is raised when an upstream is set to Origin class instance
    """

    def __init__(self):
        super(OriginWithUpstreamError, self).__init__()


class Base(Iterable, metaclass=ABCMeta):
    """Base stream class
    """

    def __init__(self):
        """Initialize Base instance
        """
        super(Base, self).__init__()
        self.__stream = None

    @property
    @abstractmethod
    def upstream(self):
        """return upstream of this instance or None
        """
        pass

    @upstream.setter
    def upstream(self, s):
        """set the upstream of this instance

        :param s: instance of Base class
        """
        pass

    @property
    def stream(self):
        """return iterator of this instance. if it is not initialized,
        initialize.
        """
        if self.__stream is None:
            self.__initialize()
        return self.__stream

    def then(self, downstream):
        """join downstream and this stream. return downstream

        :param downstream: Pipe instance
        """
        downstream.upstream = self
        return downstream

    def __gt__(self, other):
        """call .then method and return the same value

        :param other: Pipe instance
        """
        return self.then(other)

    def __initialize(self):
        """private method which is called when the stream is initialized.
        """
        if self.__stream is None:
            if self.upstream is not None:
                self.upstream.__initialize()
            self.__stream = self._initialize()
        return self.__stream

    @abstractmethod
    def _initialize(self):
        """initialization method for inherit classes of Base. This must be
        overrriden.
        """
        pass

    def __iter__(self):
        return self.stream

    def __next__(self):
        return next(self.stream)

    def run(self, hook=None):
        if hook is None:
            for x in self.stream:
                pass
        else:
            for x in self.stream:
                hook(x)
        return self


class Origin(Base):
    def __init__(self, iterable):
        super(Origin, self).__init__()
        self.__origin = iterable

    @property
    def origin(self):
        return self.__origin

    @property
    def upstream(self):
        return None

    @upstream.setter
    def upstream(self, s):
        raise OriginWithUpstreamException()

    def _initialize(self):
        yield from self.__origin

    def __getattr__(self, name):
        return self.__origin.__getattribute__(name)

    def __enter__(self):
        if hasattr(self.__origin, '__enter__') and \
                callable(self.__origin.__enter__):
            return self.__origin.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        if hasattr(self.__origin, '__exit__') and \
                hasattr(self.__origin.__exit__, '__call__'):
            return self.__origin.__exit__(type, value, traceback)
        return True


class FileReadStream(Origin):
    def __init__(self, file_name, encoding=None):
        super(FileReadStream, self).__init__(
            open(file_name, encoding=encoding or 'utf-8', mode='r')
        )


class FileWriteStream(Pipe):
    def __init__(self, file_name, encoding=None):
        super(FileWriteStream, self).__init__(
            open(file_name, encoding=encoding or 'utf-8', mode='w')
        )


class Pipe(Base):
    def __init__(self):
        super(Pipe, self).__init__()
        self.__upstream = None

    @property
    def upstream(self):
        if self.__upstream is None:
            raise EmptyPipeException()
        return self.__upstream

    @upstream.setter
    def upstream(self, s):
        if self.__upstream is None:
            self.__upstream = s
        else:
            self.__upstream.upstream = s

    def __getattr__(self, name):
        if self.__upstream is None:
            raise AttributeError(self.__class__, name)
        try:
            return self.__upstream.__getattribute__(name)
        except AttributeError:
            pass
        return self.__upstream.__getattr__(name)

    def __enter__(self):
        self.upstream.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        return self.upstream.__exit__(type, value, traceback)


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
