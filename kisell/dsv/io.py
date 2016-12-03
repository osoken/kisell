# -*- coding: utf-8 -*-

from io import StringIO
import csv

from .. core import Pipe
from .. util import CompoOrigin, CompoPipe
from .. io import FileReadStream, FileWriteStream


class DSVParse(Pipe):
    """DSV Stream class
    """
    def __init__(self, delimiter, lineterminator=None, dialect=None,
                 **kwargs):
        super(DSVParse, self).__init__()
        self.delimiter = delimiter
        self.lineterminator = lineterminator
        self.dialect = dialect
        self.kwargs = kwargs
        self.__field = None

    @property
    def field(self):
        if self.__field is not None:
            return self.__field
        if self.upstream is None:
            return None
        self.stream
        return self.__field

    def _initialize(self):
        s = csv.reader(self.upstream, delimiter=self.delimiter,
                       lineterminator=self.lineterminator,
                       dialect=self.dialect, **self.kwargs)
        self.__field = next(s)
        return s


class CSVParse(DSVParse):
    """CSV parse string upstream
    """
    def __init__(self):
        super(CSVParse, self).__init__(',', '\n', 'excel')


class TSVParse(DSVParse):
    """TSV parse string upstream
    """
    def __init__(self):
        super(TSVParse, self).__init__('\t', '\n', 'excel')


class DSVFormat(Pipe):
    """From DSV to record string.
    """
    def __init__(self, delimiter, lineterminator=None, dialect=None,
                 **kwargs):
        super(DSVFormat, self).__init__()
        self.delimiter = delimiter
        self.lineterminator = lineterminator
        self.dialect = dialect
        self.kwargs = kwargs

    def _initialize(self):
        string_out = StringIO()
        writer = csv.writer(string_out, delimiter=self.delimiter,
                            lineterminator=self.lineterminator,
                            dialect=self.dialect, **self.kwargs)
        try:
            writer.writerow(self.field)
            string_out.seek(0)
            yield string_out.read()
        except AttributeError as e:
            pass
        for x in self.upstream:
            if string_out.tell() > 256 * 1024 * 1024:
                string_out.close()
                string_out = StringIO()
                writer = csv.writer(string_out, delimiter=self.delimiter,
                                    lineterminator=self.lineterminator,
                                    dialect=self.dialect, **self.kwargs)
            pos = string_out.tell()
            writer.writerow(x)
            string_out.seek(pos)
            yield string_out.read()


class CSVFormat(DSVFormat):
    def __init__(self):
        super(CSVFormat, self).__init__(',', '\n', 'excel')


class TSVFormat(DSVFormat):
    def __init__(self):
        super(TSVFormat, self).__init__('\t', '\n', 'excel')


class DSVFileReader(CompoOrigin):
    def __init__(self, name, delimiter, encoding='utf-8', lineterminator=None,
                 dialect=None, **kwargs):
        super(DSVFileReader, self).__init__(
            FileReadStream(name, encoding),
            DSVParse(delimiter, lineterminator, dialect, **kwargs)
        )


class CSVFileReader(DSVFileReader):
    def __init__(self, name, encoding='utf-8'):
        super(CSVFileReader, self).__init__(name, ',', encoding, '\n', 'excel')


class TSVFileReader(DSVFileReader):
    def __init__(self, name, encoding='utf-8'):
        super(TSVFileReader, self).__init__(name, '\t', encoding, '\n',
                                            'excel')


class DSVFileWriter(CompoPipe):
    def __init__(self, name, delimiter, encoding='utf-8', lineterminator=None,
                 dialect=None, **kwargs):
        super(DSVFileWriter, self).__init__(
            DSVFormat(delimiter, lineterminator, dialect, **kwargs),
            FileWriteStream(name, encoding, lineterminator='')
        )


class CSVFileWriter(DSVFileWriter):
    def __init__(self, name, encoding='utf-8'):
        super(CSVFileWriter, self).__init__(name, ',', encoding, '\n', 'excel')


class TSVFileWriter(DSVFileWriter):
    def __init__(self, name, encoding='utf-8'):
        super(TSVFileWriter, self).__init__(name, '\t', encoding, '\n',
                                            'excel')
