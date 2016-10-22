# -*- coding: utf-8 -*-

from . core import Origin, Pipe


class FileReadStream(Origin):
    """``FileReadStream`` is a file input stream wrapped by
    ``kisell.core.Origin``.

    :param name: file name
    :param encoding: file encoding (default: utf-8)

    """
    def __init__(self, name, encoding=None):
        super(FileReadStream, self).__init__(
            open(name, encoding=encoding or 'utf-8', mode='r')
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
