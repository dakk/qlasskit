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

from qlasskit import qlassf

from ..utils import COMPILATION_ENABLED, qiskit_measure_and_count


class TestQlassfHybridQuantum(unittest.TestCase):
    def test_h(self):
        f = "def test(a: bool) -> bool:\n\treturn Q.H(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, uncompute=False)
        count = qiskit_measure_and_count(qf.circuit().export(), 128)
        [self.assertEqual(x in count, True) for x in ["0", "1"]]

    # THIS IS NOT ALLOWED, since hybrid quantum is applicable only with gates that
    # operates on 1 qubit a possible solution is to implement QFT directly as hybrid function.
    # def test_qft(self):
    #     f = "def test(a: Qint[2]) -> Qint[2]:\n\treturn Q.QFT(a)"
    #     qf = qlassf(f, to_compile=False, uncompute=False)
    #     print(qf.expressions)
    #     count = qiskit_measure_and_count(qf.circuit().export(), 128)
    #     [self.assertEqual(x in count, True) for x in ["00", "11", "01", "11"]]

    def test_h_multi(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\treturn Q.H(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, uncompute=False)
        count = qiskit_measure_and_count(qf.circuit().export(), 128)
        [self.assertEqual(x in count, True) for x in ["00", "11", "01", "11"]]

    def test_bell(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn Q.CX(Q.H(a), b)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, uncompute=False)
        count = qiskit_measure_and_count(qf.circuit().export(), 1024)
        [self.assertEqual(x in count, True) for x in ["00", "11"]]
        self.assertEqual(len(count.keys()), 2)

    def test_h_and_add(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\ta = Q.H(a)\n\treturn a + 1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, uncompute=False)
        count = qiskit_measure_and_count(qf.circuit().export(), 128)
        [self.assertEqual(x in count, True) for x in ["1110", "0011", "1001", "0100"]]
