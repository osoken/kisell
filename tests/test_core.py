# -*- coding: utf-8 -*-

import unittest

from kisell import core


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


if __name__ == '__main__':
    unittest.main()
