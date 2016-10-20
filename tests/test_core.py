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


if __name__ == '__main__':
    unittest.main()
