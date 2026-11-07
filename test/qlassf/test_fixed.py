# Copyright (C) 2023-2026 Davide Gessa
# This file is part of Qlasskit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest

from parameterized import parameterized, parameterized_class

from qlasskit import qlassf
from qlasskit.types import Qfixed1_3, Qfixed2_3, Qfixed2_4, Qint2, bin_to_bool_list

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
            # (Qfixed2_3, "00000", 4.0),
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

    @parameterized.expand(
        [
            [Qfixed2_3, 0.5, 0.5],
            [Qfixed2_3, 0.75, 0.75],
            [Qfixed2_3, 1.0, 0.75],
            [Qfixed2_3, 1.0, 0.5],
            [Qfixed2_3, 3.5, 0.5],
        ]
    )
    def test_fixed_add_sub(self, qft, a, b):
        self.assertEqual(qft.add(qft.const(a), qft.const(b))[1], qft.const(a + b)[1])
        self.assertEqual(qft.sub(qft.const(a), qft.const(b))[1], qft.const(a - b)[1])

    @parameterized.expand(
        [
            [Qfixed2_3, 0.5, Qint2, 2],
            [Qfixed2_3, 0.5, Qint2, 0],
        ]
    )
    def test_fixed_mul(self, qft, a, qit, b):
        self.assertEqual(qft.mul(qft.const(a), qit.const(b))[1], qft.const(a * b)[1])


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

    def test_equal_const(self):
        f = "def test(a: Qfixed[2,4]) -> bool:\n\treturn a == Qfixed2_4(0.5)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

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

    def test_gt_const(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> bool:\n\treturn a > Qfixed1_4(0.5)"
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

    def test_add_const(self):
        f = "def test(a: Qfixed[2,4]) -> Qfixed[2, 4]:\n\treturn Qfixed2_4(0.5) + a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_add(self):
        f = "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> Qfixed[1,4]:\n\treturn a + b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_mul(self):
        f = "def test(a: Qfixed[1,4]) -> Qfixed[1,4]:\n\treturn a * 3"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_sub(self):
        f = (
            "def test(a: Qfixed[1,4], b: Qfixed[1,4]) -> Qfixed[1,4]:\n"
            "\treturn a - b if a > b else b - a"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_sub_const(self):
        # TODO: allow negative overflow
        f = (
            "def test(a: Qfixed[2,4]) -> Qfixed[2, 4]:\n"
            "\treturn (a - Qfixed2_4(0.5)) if a > Qfixed2_4(0.5) else 0"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # def test_to_int(self):
    #     f = "def test(a: Qfixed[2,4]) -> Qint[2]:\n\treturn int(a)"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    # def test_to_float(self):
    #     f = "def test(a: Qint[2]) -> Qfixed[2,4]:\n\treturn float(a)"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)
