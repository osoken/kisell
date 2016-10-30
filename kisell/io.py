# -*- coding: utf-8 -*-

import tempfile

from builtins import open

from . core import Origin, Pipe


class ReadStream(Origin):
    """``ReadStream`` is an input stream wrapped by ``kisell.core.Origin``.

    :param readable: readable object
    :param buffer_size: size of buffer (default: 4096)
    """

    @classmethod
    def __generator(cls, buffer_size):
        def f(readable):
            while True:
                buf = readable.read(buffer_size)
                if len(buf) != 0:
                    yield buf
                else:
                    break
        return f

    def __init__(self, readable, buffer_size=4096):
        super(ReadStream, self).__init__(
            readable, self.__class__.__generator(buffer_size)
        )


class FileReadStream(Origin):
    """``FileReadStream`` is a file input stream wrapped by
    ``kisell.core.Origin``.

    :param name: file name
    :param encoding: file encoding (default: utf-8)
    """
    def __init__(self, name, encoding='utf-8'):
        super(FileReadStream, self).__init__(
            open(name, encoding=encoding, mode='r')
        )


class WriteStream(Pipe):
    """``WriteStream`` is an output stream. Write each line into ``writable``.
    On each iteration, it consumes one element and write it to the ``writable``
    and yields ``None``.

    :param writable: writable object
    :param lineterminator: line terminator (default: ``\\n``). specify ``''``
    not to add lineterminator
    """
    def __init__(self, writable, lineterminator='\n'):
        super(WriteStream, self).__init__(writable)
        self.__writable = writable
        self.lineterminator = lineterminator

    def _initialize(self):
        for x in self.upstream:
            self.__writable.write(x + self.lineterminator)
            yield None


class FileWriteStream(WriteStream):
    """``FileWriteStream`` is a file output stream.

    :param name: file name
    :param encoding: file encoding (defautl: utf-8)
    :param lineterminator: line end character (default: ``\\n'')
    """
    def __init__(self, name, encoding='utf-8', lineterminator='\n'):
        super(FileWriteStream, self).__init__(
            open(name, encoding=encoding, mode='w'),
            lineterminator=lineterminator
        )
