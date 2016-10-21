# -*- coding: utf-8 -*-

from collections import Iterable
from abc import ABCMeta, abstractmethod

import six


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
    """This exception is raised when an upstream is set to Origin class
    instance
    """

    def __init__(self):
        super(OriginWithUpstreamError, self).__init__()


@six.add_metaclass(ABCMeta)
class Base(six.Iterator):
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
    @abstractmethod
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

    def __add__(self, other):
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

    @abstractmethod
    def _initialize(self):
        """initialization method for inherit classes of Base. This must be
        overrriden.
        """
        pass

    def __iter__(self):
        """return stream
        """
        for x in self.stream:
            yield x

    def __next__(self):
        """return next of the stream
        """
        return next(self.stream)

    def run(self, hook=None):
        """just run through the loop

        :param hook: one-argument function
        """
        if hook is None:
            for x in self.stream:
                pass
        else:
            for x in self.stream:
                hook(x)
        return self


class Origin(Base):
    """The base class of ``kisell`` class with no upstream.
    """
    def __init__(self, iterable):
        """Initialize Origin object.

        :param iterable: an iterable
        """
        super(Origin, self).__init__()
        if not isinstance(iterable, Iterable):
            raise TypeError(
                '\'{}\' object is not iterable'.format(type(iterable).__name__)
            )
        self.__origin = iterable

    @property
    def origin(self):
        """return internal origin object.
        """
        return self.__origin

    @property
    def upstream(self):
        """return ``None``
        """
        return None

    @upstream.setter
    def upstream(self, s):
        """raises ``OriginWithUpstreamError``
        """
        raise OriginWithUpstreamError()

    def _initialize(self):
        """return iterator from the origin object.
        """
        return self.__origin

    def __getattr__(self, name):
        """return attribute of the origin object.
        """
        return self.__origin.__getattribute__(name)

    def __enter__(self):
        """called when object is used with ``with`` statement.
        return the return value of the origin's enter function if the origin
        has it, self otherwise.
        """
        if hasattr(self.__origin, '__enter__') and \
                callable(self.__origin.__enter__):
            return self.__origin.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        """called when exit ``with`` statement.
        """
        if hasattr(self.__origin, '__exit__') and \
                hasattr(self.__origin.__exit__, '__call__'):
            return self.__origin.__exit__(type, value, traceback)
        return True


class Pipe(Base):
    """The base class of ``kisell`` class with upstream.
    """
    def __init__(self):
        super(Pipe, self).__init__()
        self.__upstream = None

    @property
    def upstream(self):
        if self.__upstream is None:
            raise EmptyPipeError()
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
