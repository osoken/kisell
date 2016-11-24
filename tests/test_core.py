# -*- coding: utf-8 -*-

import os
import unittest

from kisell import core


_license_file_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'LICENSE'
)
_license_file_content = None
with open(_license_file_path, 'r') as f:
    _license_file_content = f.read()


class BaseTester(unittest.TestCase):

    class Concrete(core.Base):
        def __init__(self):
            super(BaseTester.Concrete, self).__init__()
            self.__upstream = None
            self.init_count = 0

        def _get_upstream(self):
            super(BaseTester.Concrete, self)._get_upstream()
            return self.__upstream

        def _set_upstream(self, s):
            super(BaseTester.Concrete, self)._set_upstream(s)
            self.__upstream = s

        def _initialize(self):
            super(BaseTester.Concrete, self)._initialize()
            self.init_count += 1
            if self.upstream is None:
                for x in range(4):
                    yield x
            else:
                for x in self.upstream:
                    yield x + 1

        upstream = property(_get_upstream, _set_upstream)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        a = []
        with self.assertRaises(TypeError):
            for x in core.Base():
                a.append(x)
        self.assertEqual(len(a), 0)
        self.assertTrue(isinstance(BaseTester.Concrete(), core.Base))

    def test_property_upstream(self):
        test = BaseTester.Concrete()
        self.assertIsNone(test.upstream)
        test.upstream = [1, 2, 3]
        self.assertIsNotNone(test.upstream)
        test.upstream = None
        self.assertIsNone(test.upstream)

    def test_property_stream(self):
        self.assertEqual(sum(BaseTester.Concrete().stream), sum(range(4)))
        self.assertEqual(sum(BaseTester.Concrete()), sum(range(4)))

    def test_then(self):
        test = BaseTester.Concrete()
        test2 = BaseTester.Concrete()
        self.assertEqual(sum(test.then(test2)), 10)
        test = BaseTester.Concrete()
        test2 = BaseTester.Concrete()
        test3 = BaseTester.Concrete()
        self.assertEqual(sum(test.then(test2).then(test3)), 14)

    def test__add__(self):
        test = BaseTester.Concrete()
        test2 = BaseTester.Concrete()
        self.assertEqual(sum(test + test2), 10)
        test = BaseTester.Concrete()
        test2 = BaseTester.Concrete()
        test3 = BaseTester.Concrete()
        self.assertEqual(sum(test + test2 + test3), 14)

    def test__initialize(self):
        test = BaseTester.Concrete()
        up = BaseTester.Concrete()
        self.assertEqual(test.init_count, 0)
        up.then(test)
        self.assertEqual(test.init_count, 0)
        self.assertEqual(up.init_count, 0)
        self.assertIsNone(up._Base__stream)
        up.stream
        self.assertIsNotNone(up._Base__stream)
        sum(test)
        self.assertEqual(test.init_count, 1)
        self.assertEqual(up.init_count, 1)

    def test__iter__(self):
        cnt = 0
        for (x, y) in zip(iter(BaseTester.Concrete()),
                          BaseTester.Concrete().__iter__()):
            self.assertEqual(x, y)
            cnt += 1
        self.assertEqual(len(list(BaseTester.Concrete())), cnt)

    def test__call__(self):
        test = BaseTester.Concrete()
        test()
        rest = list(test)
        self.assertEqual(len(rest), 0)


class OriginTester(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        test = core.Origin([1, 2, 3])
        self.assertTrue(isinstance(test, core.Base))
        self.assertTrue(isinstance(test, core.Origin))
        self.assertFalse(isinstance(test, core.Pipe))
        for (x, y) in zip([1, 2, 3], test):
            self.assertEqual(x, y)
        with self.assertRaises(TypeError):
            core.Origin(123)
        test = core.Origin('123 234 345 456', lambda x: x.split(' '))
        l = list(test)
        self.assertEqual(len(l), 4)
        self.assertEqual(l[0], '123')
        self.assertEqual(l[1], '234')
        self.assertEqual(l[2], '345')
        self.assertEqual(l[3], '456')
        self.assertEqual(test.__len__(), len('123 234 345 456'))

    def test_property_origin(self):
        range_object = range(10)
        test = core.Origin(range_object)
        self.assertEqual(range_object, test.origin)
        with self.assertRaises(AttributeError):
            test.origin = [0, 1, 2]

    def test_property_upstream(self):
        test = core.Origin('123')
        self.assertIsNone(test.upstream)
        with self.assertRaises(core.OriginWithUpstreamError):
            test.upstream = [1, 2, 3]
        with self.assertRaises(core.OriginWithUpstreamError):
            test.upstream = core.Origin([0, 1, 2])

    def test_initialize(self):
        origin = '123'
        test = core.Origin(origin)
        self.assertEqual(test.stream, origin)

    def test__getattr__(self):
        origin = 'abcde'
        test = core.Origin(origin)
        self.assertEqual(test.upper(), origin.upper())
        test.upper = lambda: test.origin[0].upper() + test.origin[1:]
        self.assertEqual(origin.upper(), 'ABCDE')
        self.assertNotEqual(origin.upper(), test.upper())
        with self.assertRaises(AttributeError):
            test.non_such_attribute
        with open(_license_file_path, 'r') as f:
            test = core.Origin(f)
            s = test.read()
            self.assertEqual(s, _license_file_content)
            test.close()
            self.assertTrue(f.closed)

    def test__enter__exit__(self):
        with core.Origin([0, 2, 4, 5]) as test:
            res = list(test)
            self.assertEqual(res[0], 0)
            self.assertEqual(res[1], 2)
            self.assertEqual(len(res), 4)
        fin = open(_license_file_path, 'r')
        with core.Origin(fin) as test:
            s = test.read()
            self.assertEqual(s, _license_file_content)
        self.assertTrue(fin.closed)


class PipeTester(unittest.TestCase):

    class ConcretePipe(core.Pipe):
        def __init__(self, base=None):
            super(PipeTester.ConcretePipe, self).__init__(base)

        def _initialize(self):
            for x in self.upstream:
                yield x + 1

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        test = PipeTester.ConcretePipe()
        self.assertIsNone(test._Pipe__upstream)

    def test__property_upstream(self):
        test = PipeTester.ConcretePipe()
        with self.assertRaises(core.EmptyPipeError):
            self.assertIsNone(test.upstream)
        p0 = PipeTester.ConcretePipe()
        p1 = PipeTester.ConcretePipe()
        p2 = PipeTester.ConcretePipe()
        p0.upstream = p1
        self.assertEqual(p1, p0.upstream)
        p0.upstream = p2
        self.assertEqual(p1, p0.upstream)
        self.assertEqual(p2, p1.upstream)
        with self.assertRaises(core.EmptyPipeError):
            self.assertIsNone(p2.upstream)

    def test__getattr__(self):
        p0 = PipeTester.ConcretePipe()
        p1 = PipeTester.ConcretePipe()
        p2 = PipeTester.ConcretePipe()
        fin = open(_license_file_path, 'r')
        p0.upstream = p1
        p0.upstream = p2
        p0.upstream = fin
        with self.assertRaises(AttributeError):
            p0.non_such_attribute
        self.assertEqual(p0.name, fin.name)
        self.assertEqual(p1.name, fin.name)
        self.assertEqual(p1.name, p0.name)
        self.assertEqual(p2.name, fin.name)
        self.assertEqual(p2.name, p0.name)
        self.assertEqual(p2.name, p1.name)
        p1.name = 'something new'
        self.assertNotEqual(p0.name, fin.name)
        self.assertNotEqual(p1.name, fin.name)
        self.assertEqual(p1.name, p0.name)
        self.assertEqual(p2.name, fin.name)
        self.assertNotEqual(p2.name, p0.name)
        self.assertNotEqual(p2.name, p1.name)
        fin.close()
        attr_base = 'abc'
        p0 = PipeTester.ConcretePipe(attr_base)
        self.assertEqual(len(attr_base), p0.__len__())
        with self.assertRaises(AttributeError):
            p0.still_non_such_attribute

    def test__enter__exit__(self):
        fin = open(_license_file_path, 'r')
        test = PipeTester.ConcretePipe()
        test.upstream = fin
        with test:
            pass
        self.assertTrue(fin.closed)
        test = PipeTester.ConcretePipe(open(_license_file_path, 'r'))
        fin = open(_license_file_path, 'r')
        test.upstream = fin
        with test:
            pass
        self.assertTrue(test.closed)


if __name__ == '__main__':
    unittest.main()
