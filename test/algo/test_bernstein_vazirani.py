# Copyright 2023-2024 Davide Gessa

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

from parameterized import parameterized_class

from qlasskit import qlassf
from qlasskit.algorithms import DeutschJozsa

from ..utils import ENABLED_COMPILERS, qiskit_measure_and_count


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestAlgoBernsteinVazirani(unittest.TestCase):
    def test_1_bernstein_vazirani(self):
        f = """
def oracle(x: Qint[4]) -> bool:
    s=Qint4(14)
    return ((x[0]&s[0])^(x[1]&s[1])^(x[2]&s[2])^(x[3]&s[3]))
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = BernsteinVazirani(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable,0111)

    def test_2_bernstein_vazirani(self):
        f = """
def oracle(x: Qint[4]) -> bool:
    s=Qint4(15)
    return ((x[0]&s[0])^(x[1]&s[1])^(x[2]&s[2])^(x[3]&s[3]))
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = BernsteinVazirani(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable,1111)

    def test_3_bernstein_vazirani(self):
        f = """
def oracle(x: Qint[4]) -> bool:
    s=Qint4(12)
    return ((x[0]&s[0])^(x[1]&s[1])^(x[2]&s[2])^(x[3]&s[3]))
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = BernsteinVazirani(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable,0011)

    def test_4_bernstein_vazirani(self):
        f = """
def oracle(x: Qint[4]) -> bool:
    s=Qint4(8)
    return ((x[0]&s[0])^(x[1]&s[1])^(x[2]&s[2])^(x[3]&s[3]))
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = BernsteinVazirani(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable,0001)

