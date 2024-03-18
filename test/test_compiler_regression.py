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
