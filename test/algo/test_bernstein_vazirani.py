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
    def test_bernstein_vazirani_balanced(self):
        f = """
def oracle(a: Qint[4]) -> bool:
    return (a[0] & True) | (a[1] & False) | (a[2] & False) | (a[3] & True)
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = BernsteinVazirani(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        #counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts)
"""     
    def test_deutschjozsa_balanced2(self):
        f = """
def hash(k: bool) -> bool:
    return k
    """
        qf = qlassf(f, compiler=self.compiler)
        algo = DeutschJozsa(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable["Balanced"], 1024)

    def test_deutschjozsa_constant(self):
        f = """
def hash(k: Qint2) -> bool:
    return False
    """
        qf = qlassf(f, compiler=self.compiler)
        algo = DeutschJozsa(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable["Constant"], 1024)
"""        
