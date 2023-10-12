# Copyright 2023 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from qlasskit import Qint4, QlassF, qlassf

from . import utils
from .utils import COMPILATION_ENABLED, compute_and_compare_results

class TestQlassf(unittest.TestCase):
    def test_print_call(self):
        f = "def test(a: bool) -> bool:\n\tprint(a)\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        compute_and_compare_results(self, qf)

class TestQlassfDecorator(unittest.TestCase):
    def test_decorator(self):
        c = qlassf(utils.test_not, to_compile=False)
        self.assertTrue(isinstance(c, QlassF))


class TestQlassfTruthTable(unittest.TestCase):
    def test_not_truth(self):
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [[False, True], [True, False]],
        )

    def test_and_truth(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a and b"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [
                [False, False, False],
                [False, True, False],
                [True, False, False],
                [True, True, True],
            ],
        )

    def test_or_truth(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a or b"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [
                [False, False, False],
                [False, True, True],
                [True, False, True],
                [True, True, True],
            ],
        )

    def test_or_not_truth(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a or b"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [
                [False, False, False],
                [False, True, True],
                [True, False, True],
                [True, True, True],
            ],
        )

    def test_big_truth(self):
        f = "def test(a: Qint4) -> Qint4:\n\treturn a"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        tth = qf.truth_table_header()

        self.assertEqual(
            tth, ["a.0", "a.1", "a.2", "a.3", "_ret.0", "_ret.1", "_ret.2", "_ret.3"]
        )
        self.assertEqual(
            tt,
            [
                [False, False, False, False] * 2,
                [False, False, False, True] * 2,
                [False, False, True, False] * 2,
                [False, False, True, True] * 2,
                [False, True, False, False] * 2,
                [False, True, False, True] * 2,
                [False, True, True, False] * 2,
                [False, True, True, True] * 2,
                [True, False, False, False] * 2,
                [True, False, False, True] * 2,
                [True, False, True, False] * 2,
                [True, False, True, True] * 2,
                [True, True, False, False] * 2,
                [True, True, False, True] * 2,
                [True, True, True, False] * 2,
                [True, True, True, True] * 2,
            ],
        )

    def test_too_big_truth(self):
        f = "def test(a: Qint12) -> Qint12:\n\treturn a"
        qf = qlassf(f, to_compile=False)
        self.assertRaises(Exception, lambda: qf.truth_table())
