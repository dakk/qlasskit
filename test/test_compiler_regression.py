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

from qlasskit import boolopt, qlassf

from .utils import ENABLED_COMPILERS, compute_and_compare_results


class TestCompilerRegression(unittest.TestCase):
    def test_1(self):
        f = "def f(a: bool, b: bool) -> bool:\n\treturn a ^ (not b)"
        qc = qlassf(f, to_compile=True, compiler="internal").circuit()
        self.assertEqual(qc.num_gates, 3)
        self.assertEqual(qc.num_qubits, 3)

    def test_2(self):
        f = "def f(a: bool, b: bool) -> bool:\n\treturn a ^ (not b)"
        qc = qlassf(f, to_compile=True, compiler="internal").circuit()
        self.assertEqual(qc.num_gates, 3)
        self.assertEqual(qc.num_qubits, 3)

    def test_3(self):
        f = """def hash_simp(m: Qlist[Qint[4], 2]) -> Qint8:
    hv = 0
    for i in m:
        hv = ((hv << 4) ^ (hv >> 1) ^ i) & 0xff

    return hv"""
        qc = qlassf(f, to_compile=True, compiler="internal").circuit()
        self.assertEqual(qc.num_gates, 11)
        self.assertEqual(qc.num_qubits, 16)

    def test_4_dupqubit(self):
        f = """def test(a_list: Qlist[Qint8, 8]) -> Qint16:
    h_val = Qint16(0)
    for c in a_list:
        h_val = h_val + c
    return h_val"""

        qlassf(f, bool_optimizer=boolopt.fastOptimizer)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestCompilerRegression_Multicomp(unittest.TestCase):
    def test_1_const_return(self):
        f = "def test() -> Tuple[Qint2, Qint2]:\n\treturn [0, 1]"
        qf = qlassf(f, to_compile=True, compiler=self.compiler)
        compute_and_compare_results(self, qf)
