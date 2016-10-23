# -*- coding: utf-8 -*-

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

    def __init__(self, readable, buffer_size):
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

    :param writable: writable object
    :param lineterminator: line terminator (default: ``\\n``). ``None`` for not
    to insert line ends.
    """
    def __init__(self, writable, lineterminator='\n'):
        super(WriteStream, self).__init__()
        self.__writable = writable
        self.lineterminator = lineterminator

    def _initialize(self):
        for x in self.upstream:
            self.__writable.write(x)
            if self.lineterminator is not None:
                self.__writable.write(self.lineterminator)

    def __getattr__(self, name):
        try:
            return self.__writable.__getattribute__(name)
        except AttributeError:
            pass
        return super(WriteStream, self).__getattr__(name)
