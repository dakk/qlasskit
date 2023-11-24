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

from qlasskit import Qint2, Qint4, qlassf
from qlasskit.algorithms import Grover

from .utils import qiskit_measure_and_count


class TestAlgoGrover(unittest.TestCase):
    def test_grover(self):
        f = """
def hash(k: Qint4) -> bool:
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
def hash(k: Qint4) -> bool:
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
def hash(k: Qint4) -> bool:
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
def hash(k: Qint4, q: Qint4) -> bool:
    h = True
    for i in range(4):
        h = h and (k[i] or q[i])
    return h
"""
        qf = qlassf(f)

        self.assertRaises(Exception, lambda x: Grover(x), qf)

    def test_grover_subset_sum(self):
        f = """
def subset_sum(ii: Tuple[Qint2, Qint2]) -> Qint2:
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
