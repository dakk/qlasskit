# Copyright 2024 Davide Gessa

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

from parameterized import parameterized, parameterized_class

from qlasskit import qlassf
from qlasskit.types.qfixed import Qfixed1_3, Qfixed2_3, Qfixed2_4
from qlasskit.types.qtype import bin_to_bool_list

from ..utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


class TestQfixedEncoding(unittest.TestCase):
    @parameterized.expand(
        [
            (Qfixed1_3, "0110", 0.75),
            (Qfixed1_3, "0100", 0.5),
            (Qfixed1_3, "0010", 0.25),
            (Qfixed1_3, "1000", 1.0),
            (Qfixed2_3, "01000", 2.0),
            (Qfixed2_3, "01100", 2.5),
        ]
    )
    def test_fixed_from_bool_and_to_bin(self, qft, bin_v, val):
        self.assertEqual(qft.from_bool(bin_to_bool_list(bin_v)), val)
        self.assertEqual(qft.to_bin(qft(val)), bin_v)

    @parameterized.expand(
        [
            [Qfixed2_3, 3.75, 1.75, True],
            [Qfixed2_3, 1.0, 2.0, False],
            [Qfixed2_3, 0.0, 2.0, False],
            [Qfixed2_4, 0.2, 0.3, False],
            [Qfixed2_4, 0.1, 0.05, True],
            [Qfixed2_4, 0.1, 0.2, False],
            [Qfixed2_4, 0.6, 0.4, True],
        ]
    )
    def test_fixed_gt(self, qft, a, b, r):
        self.assertEqual(qft.gt(qft.const(a), qft.const(b))[1], r)
        self.assertEqual(qft.lt(qft.const(a), qft.const(b))[1], not r)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQfixed(unittest.TestCase):
    def test_fixed_identity(self):
        f = "def test(a: Qfixed[1, 3]) -> Qfixed[1, 3]:\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_fixed_const(self):
        f = "def test() -> Qfixed[1, 3]:\n\treturn 0.1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # def test_equal_const(self):
    #     f = "def test(a: Qfixed[1,4]) -> bool:\n\treturn a == 0.1"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    def test_equal(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> bool:\n\treturn a == b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_not_equal(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> bool:\n\treturn a != b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_gt(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> bool:\n\treturn a > b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_lt(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> bool:\n\treturn a < b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_lte(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> bool:\n\treturn a <= b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_gte(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> bool:\n\treturn a >= b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # def test_sum_const(self):
    #     f = "def test(a: Qfixed[1,4]) -> Qfixed[1, 3]:\n\treturn 0.1 + a"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)
