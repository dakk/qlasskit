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

from qlasskit import Qint2, qlassf
from qlasskit.algorithms import Grover

from ..utils import qiskit_measure_and_count


class TestAlgoGrover(unittest.TestCase):
    def test_grover(self):
        f = """
def hash(k: Qint[4]) -> bool:
    h = True
    for i in range(4):
        h = h and k[i]
    return h
"""
        qf = qlassf(f)
        algo = Grover(qf, True)

        qc = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc, shots=1024)
        counts_readable = algo.decode_counts(counts)

        self.assertEqual(15 in counts_readable, True)
        self.assertEqual(algo.output_qubits, [0, 1, 2, 3])
        self.assertEqual(counts_readable[15] > 600, True)

    def test_grover_list_search(self):
        f = """
def hash(k: Qint[4]) -> bool:
    h = False
    for i in [7]:
        if i == k:
            h = True
    return h
"""
        qf = qlassf(f)
        algo = Grover(qf, True)

        qc = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc, shots=1024)
        counts_readable = algo.decode_counts(counts)

        self.assertEqual(15 in counts_readable, True)
        self.assertEqual(algo.output_qubits, [0, 1, 2, 3])
        self.assertEqual(counts_readable[7] > 600, True)

    def test_grover_without_element_to_search(self):
        f = """
def hash(k: Qint[4]) -> bool:
    h = True
    for i in range(4):
        h = h and k[i]
    return h
"""
        qf = qlassf(f)
        algo = Grover(qf)

        qc = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc, shots=1024)
        counts_readable = algo.decode_counts(counts)

        self.assertEqual(15 in counts_readable, True)
        self.assertEqual(counts_readable[15] > 600, True)

    def test_grover_too_many_args(self):
        f = """
def hash(k: Qint[4], q: Qint[4]) -> bool:
    h = True
    for i in range(4):
        h = h and (k[i] or q[i])
    return h
"""
        qf = qlassf(f)

        self.assertRaises(Exception, lambda x: Grover(x), qf)

    def test_grover_subset_sum(self):
        f = """
def subset_sum(ii: Tuple[Qint[2], Qint[2]]) -> Qint[2]:
    l = [0, 1, 2, 0]
    return l[ii[0]] + l[ii[1]]
"""
        qf = qlassf(f)
        algo = Grover(qf, Qint2(3))

        qc = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc, shots=1024)
        counts_readable = algo.decode_counts(counts)

        self.assertEqual((1, 2) in counts_readable, True)
        self.assertEqual(counts_readable[(1, 2)] > 300, True)
        self.assertEqual(counts_readable[(2, 1)] > 300, True)
