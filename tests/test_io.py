# -*- coding: utf-8 -*-

import os
import unittest

from kisell.core import Pipe
from kisell import io


_license_file_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'LICENSE'
)
_license_file_content = None
with open(_license_file_path, 'r') as f:
    _license_file_content = f.read()


class _AddLineNumber(Pipe):
    def __init__(self):
        super(_AddLineNumber, self).__init__()

    def _initialize(self):
        cnt = 0
        for x in self.upstream:
            yield str(cnt) + x
            cnt += 1


class ReadStreamTester(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        fin = open(_license_file_path, 'r')
        test = rw.ReadStream(fin, 100)
        l = list(test)
        self.assertEqual(len(l[0]), 100)


class FileReadStreamTester(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        test = rw.FileReadStream(_license_file_path)
        self.assertEqual(test.name, _license_file_path)
        self.assertEqual(test.encoding, 'utf-8')
        self.assertEqual(test.mode, 'r')
        content = test.read()
        self.assertEqual(content, _license_file_content)


class WriteStreamTester(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        pass


class FileWriteStreamTester(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        pass
