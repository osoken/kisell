# -*- coding: utf-8 -*-

import os
import re
import unittest

from kisell.core import Origin, Pipe
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
        test = io.ReadStream(fin, 100)
        l = list(test)
        self.assertEqual(len(l[0]), 100)


class FileReadStreamTester(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        test = io.FileReadStream(_license_file_path)
        self.assertEqual(test.name, _license_file_path)
        self.assertEqual(test.encoding, 'utf-8')
        self.assertEqual(test.mode, 'r')
        content = test.read()
        self.assertEqual(content, _license_file_content)


class WriteStreamTester(unittest.TestCase):

    tmp_dir_path = os.path.join(os.path.dirname(__file__), 'tmp')

    def setUp(self):
        if not os.path.exists(WriteStreamTester.tmp_dir_path):
            os.makedirs(WriteStreamTester.tmp_dir_path)

    def tearDown(self):
        os.removedirs(WriteStreamTester.tmp_dir_path)

    def test__init__(self):
        tmp_name = os.path.join(WriteStreamTester.tmp_dir_path, 'init')
        tmp_file = open(tmp_name, 'w')
        test = io.WriteStream(tmp_file)
        orig = Origin(re.split('\s', _license_file_content))
        (orig + test).run()
        tmp_file.close()
        with open(tmp_name, 'r') as tmp_fin:
            self.assertListEqual([x.rstrip('\n') for x in tmp_fin],
                                 re.split('\s', _license_file_content))
        os.remove(tmp_name)


class FileWriteStreamTester(unittest.TestCase):
    pass
