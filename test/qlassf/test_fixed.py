# Copyright 2024 Davide Gessa

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

from qlasskit import Qfixed, qlassf
from qlasskit.types import Qfixed1_3

from ..utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


class TestQlassfFixed(unittest.TestCase):
    def test_fixed_const(self):
        self.assertEqual(Qfixed1_3.to_bin(Qfixed1_3(0.3)), "0110")
        self.assertEqual(Qfixed1_3.to_bin(Qfixed1_3(0.1)), "0010")
        self.assertEqual(Qfixed1_3.to_bin(Qfixed1_3(0.2)), "0100")
        self.assertEqual(Qfixed1_3.to_bin(Qfixed1_3(1.0)), "0001")

    def test_fixed_from_bool(self):
        def fb(b):
            return list(map(lambda c: True if c == "1" else False, b))

        self.assertEqual(Qfixed1_3.from_bool(fb("0110")), 0.3)
        self.assertEqual(Qfixed1_3.from_bool(fb("0010")), 0.1)
        self.assertEqual(Qfixed1_3.from_bool(fb("0100")), 0.2)
        self.assertEqual(Qfixed1_3.from_bool(fb("0001")), 1.0)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfFixed2(unittest.TestCase):
    def test_fixed_identity(self):
        f = "def test(a: Qfixed[1, 3]) -> Qfixed[1, 3]:\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_fixed_const(self):
        f = "def test() -> Qfixed[1, 3]:\n\treturn 0.1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # def test_sum_const(self):
    #     f = "def test(a: Qfixed[2,2]) -> Qfixed[2, 2]:\n\treturn 0.1 + a"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)
