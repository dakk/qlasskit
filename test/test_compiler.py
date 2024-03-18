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
