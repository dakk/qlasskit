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

from parameterized import parameterized_class

from qlasskit import qlassf

from .utils import ENABLED_COMPILERS, compute_and_compare_results


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestCompiler(unittest.TestCase):
    def test_not_arg(self):
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_and(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a and b"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_and_long(self):
        f = "def test(a: bool, b: bool, c: bool, d: bool) -> bool:\n\treturn a and b and c and d"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_and_long_with_not(self):
        f = (
            "def test(a: bool, b: bool, c: bool, d: bool) -> bool:\n\t"
            "return a and b and not c and d"
        )
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_or(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a or b"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_or_not(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn not a or b"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_edge_case_not_inside_xor(self):
        f = "def f1(a: bool, b: bool, c: bool) -> bool:\n\treturn (b and a) ^ (not (c))"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        self.assertEqual(qf.circuit().num_qubits, 4)
        self.assertEqual(qf.circuit().num_gates, 3)
        compute_and_compare_results(self, qf)

    def test_edge_case_not_inside_xor2(self):
        f = "def f1(a: bool, b: bool, c: bool) -> bool:\n\treturn (b and a) ^ (not (b ^ c))"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        self.assertEqual(qf.circuit().num_qubits, 4)
        self.assertEqual(qf.circuit().num_gates, 4)
        compute_and_compare_results(self, qf)

    def test_sum_and_sub(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n" "\treturn (a + 3) - 3"
        qf = qlassf(f, to_compile=True, compiler=self.compiler, uncompute=True)
        # print(qf.expressions)
        # qf.circuit().draw()
        compute_and_compare_results(self, qf)


# class TestInternalCompiler(unittest.TestCase):
