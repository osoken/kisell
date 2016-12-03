# -*- coding: utf-8 -*-

from functools import reduce
from collections import Iterable
import re
import operator

from .. core import Pipe


class _ResolveTargetField(object):
    """Mix-in class.
    """

    def _resolve_target_field(self, field, target_field):
        if isinstance(target_field, (str, bytes, re._pattern_type)):
            res = set()
            for i, f in enumerate(field):
                m = re.match(target_field, f)
                if m is not None and m.span()[1] == len(f):
                    res.add(i)
            return res
        if isinstance(target_field, int):
            return set(tuple(target_field))
        if isinstance(target_field, Iterable):
            return reduce(lambda x, y: x.union(y), (
                self._resolve_target_field(field, tf) for tf in target_field
            ))


class Filter(Pipe, _ResolveTargetField):
    """Filter records by the condition that the ``target_field`` of the record
    satisfies ``filterfunc``.

    :param filterfunc: one-argument function which returns a boolean
    :param target_field: field name, field index, regular expression or
    tuple of them.
    """
    def __init__(self, filterfunc, target_field):
        super(Filter, self).__init__()
        self.filterfunc = filterfunc
        self.target_field = target_field

    def __construct_filter(self):
        fields = self._resolve_target_field(self.field, self.target_field)
        if len(fields) == 0:
            return lambda x: True
        if len(fields) == 1:
            i = tuple(fields)[0]
            return lambda x: self.filterfunc(x[i])
        return lambda x: reduce(
            operator.and_, (self.filterfunc(x[i]) for i in fields)
        )

    def _initialize(self):
        ff = self.__construct_filter()
        for x in self.upstream:
            if ff(x):
                yield x


class Map(Pipe, _ResolveTargetField):
    """Generate records applying ``func`` to the ``target_field`` of the
    record.

    :param func: one-argument function which returns a boolean
    :param target_field: field name, field index, regular expression or
    tuple of them.
    """
    def __init__(self, func, target_field):
        super(Map, self).__init__()
        self.func = func
        self.target_field = target_field

    def __construct_map(self):
        fields = self._resolve_target_field(self.field, self.target_field)
        return lambda record: [
            self.func(x) if i in fields else x for (i, x) in enumerate(record)
        ]

    def _initialize(self):
        mf = self.__construct_map()
        for x in self.upstream:
            yield mf(x)


class ToMapping(Pipe):
    """Convert each record to mapping.
    """
    def __init__(self):
        super(ToMapping, self).__init__()

    def _initialize(self):
        for x in self.upstream:
            yield {
                f: v for (f, v) in zip(self.field, x)
            }


class GroupBy(Pipe, _ResolveTargetField):
    """Generate sub generators
    """


class Select(Pipe, _ResolveTargetField):
    """Select fields.

    :param target_field: field name, field index, regular expression or
    tuple of them.
    """
    def __init__(self, target_field):
        super(Select, self).__init__()
        self.target_field = target_field
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
        fields = self._resolve_target_field(self.upstream.field,
                                            self.target_field)
        self.__field = [self.upstream.field[i] for i in fields]
        for x in self.upstream:
            yield [x[i] for i in fields]


class Deselect(Pipe, _ResolveTargetField):
    """Deselect fields.

    :param target_field: field name, field index, regular expression or
    tuple of them.
    """
    def __init__(self, target_field):
        super(Select, self).__init__()
        self.target_field = target_field
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
        fields = [
            i for i in range(len(self.field))
            if i not in self._resolve_target_field(self.upstream.field,
                                                   self.target_field)
        ]
        self.__field = [self.upstream.field[i] for i in fields]
        for x in self.upstream:
            yield [x[i] for i in fields]
