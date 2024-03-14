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
from sympy import Symbol, symbols
from sympy.logic import And

from qlasskit import qlassf

from ..utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfFixed2(unittest.TestCase):
    def test_fixed_const(self):
        f = "def test() -> Qfixed[2, 2]:\n\treturn 0.1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # def test_sum(self):
    #     f = "def test(a: Qfixed[2,2]) -> Qfixed[2, 2]:\n\treturn 0.1 + a"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)
