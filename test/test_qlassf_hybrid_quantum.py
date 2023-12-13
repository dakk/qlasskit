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

from parameterized import parameterized_class

from qlasskit import QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, ENABLED_COMPILERS, qiskit_measure_and_count


class TestQlassfHybridQuantum(unittest.TestCase):
    def test_h(self):
        f = "def test(a: bool) -> bool:\n\treturn Q.H(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, uncompute=False)
        count = qiskit_measure_and_count(qf.circuit().export(), 128)
        [self.assertEqual(x in count, True) for x in ["0", "1"]]

    def test_h_multi(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn Q.H(a)"
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
        f = "def test(a: Qint2) -> Qint2:\n\ta = Q.H(a)\n\treturn a + 1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, uncompute=False)
        count = qiskit_measure_and_count(qf.circuit().export(), 128)
        [self.assertEqual(x in count, True) for x in ["1110", "0011", "1001", "0100"]]
