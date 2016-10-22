# -*- coding: utf-8 -*-

import unittest

from kisell import core


class BaseTester(unittest.TestCase):

    class Concrete(core.Base):
        def __init__(self):
            super(BaseTester.Concrete, self).__init__()
            self.__upstream = None
            self.init_count = 0

        @property
        def upstream(self):
            return self.__upstream

        @upstream.setter
        def upstream(self, s):
            self.__upstream = s

        def _initialize(self):
            self.init_count += 1
            if self.upstream is None:
                for x in range(4):
                    yield x
            else:
                for x in self.upstream:
                    yield x + 1

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

    def test_run(self):
        test = BaseTester.Concrete()
        test.run()
        rest = list(test)
        self.assertEqual(len(rest), 0)

        res = []

        def push(x):
            res.append(x)

        test = BaseTester.Concrete()
        test.run(push)
        rest = list(test)
        self.assertEqual(len(rest), 0)
        self.assertEqual(len(res), len(list(BaseTester.Concrete())))


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
            test.nonsuch




if __name__ == '__main__':
    unittest.main()
