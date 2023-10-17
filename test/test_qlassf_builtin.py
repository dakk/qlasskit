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
from typing import Tuple

from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, compute_and_compare_results


class TestQlassfBuiltinFunctions(unittest.TestCase):
    def test_print_call(self):
        f = "def test(a: bool) -> bool:\n\tprint(a)\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        compute_and_compare_results(self, qf)

    def test_len(self):
        f = "def test(a: Tuple[bool, bool]) -> Qint2:\n\treturn len(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(qf.expressions[0][1], False)
        self.assertEqual(qf.expressions[1][1], True)
        compute_and_compare_results(self, qf)

    def test_len4(self):
        f = "def test(a: Tuple[bool, bool, bool, bool]) -> Qint4:\n\treturn len(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(qf.expressions[0][1], False)
        self.assertEqual(qf.expressions[1][1], False)
        self.assertEqual(qf.expressions[2][1], True)
        self.assertEqual(qf.expressions[3][1], False)
        compute_and_compare_results(self, qf)


    # def test_max(self):
    #     f = "def test(a: Qint2, b: Qint2) -> Qint2:\n\treturn max(a,b)"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED)
    #     compute_and_compare_results(self, qf)
        
    # def test_max_tuple(self):
    #     f = "def test(a: Tuple[Qint2, Qint2]) -> Qint2:\n\treturn max(a)"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED)
    #     compute_and_compare_results(self, qf)
