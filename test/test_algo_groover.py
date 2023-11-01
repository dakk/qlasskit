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
from qlasskit.algorithms import Groover

from .utils import qiskit_measure_and_count


class TestAlgoGroover(unittest.TestCase):
    def test_groover(self):
        f = """
def hash(k: Qint4) -> bool:
    h = True
    for i in range(4):
        h = h and k[i]
    return h
"""
        qf = qlassf(f)
        algo = Groover(qf, True)

        qc = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc, shots=1024)
        counts_readable = algo.interpet_counts(counts)

        self.assertEqual(15 in counts_readable, True)
        self.assertEqual(algo.out_qubits(), [0, 1, 2, 3])
        self.assertEqual(counts_readable[15] > 600, True)

    def test_groover_without_element_to_search(self):
        f = """
def hash(k: Qint4) -> bool:
    h = True
    for i in range(4):
        h = h and k[i]
    return h
"""
        qf = qlassf(f)
        algo = Groover(qf)

        qc = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc, shots=1024)
        counts_readable = algo.interpet_counts(counts)

        self.assertEqual(15 in counts_readable, True)
        self.assertEqual(counts_readable[15] > 600, True)

    def test_groover_too_many_args(self):
        f = """
def hash(k: Qint4, q: Qint4) -> bool:
    h = True
    for i in range(4):
        h = h and (k[i] or q[i])
    return h
"""
        qf = qlassf(f)

        self.assertRaises(Exception, lambda x: Groover(x), qf)
