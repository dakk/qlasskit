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

from parameterized import parameterized_class
from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfBuiltinFunctions(unittest.TestCase):
    def test_print_call(self):
        f = "def test(a: bool) -> bool:\n\tprint(a)\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        compute_and_compare_results(self, qf)

    def test_len(self):
        f = "def test(a: Tuple[bool, bool]) -> Qint2:\n\treturn len(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[0][1], False)
        self.assertEqual(qf.expressions[1][1], True)
        compute_and_compare_results(self, qf)

    def test_len2(self):
        f = "def test(a: Tuple[bool, bool]) -> Qint2:\n\tc=a\n\treturn len(c)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-2][1], False)
        self.assertEqual(qf.expressions[-1][1], True)
        compute_and_compare_results(self, qf)

    def test_len4(self):
        f = "def test(a: Tuple[bool, bool, bool, bool]) -> Qint4:\n\treturn len(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[0][1], False)
        self.assertEqual(qf.expressions[1][1], False)
        self.assertEqual(qf.expressions[2][1], True)
        self.assertEqual(qf.expressions[3][1], False)
        compute_and_compare_results(self, qf)

    def test_min(self):
        f = "def test(a: Qint2, b: Qint2) -> Qint2:\n\treturn min(a,b)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_min_const(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn min(a,3)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_max(self):
        f = "def test(a: Qint2, b: Qint2) -> Qint2:\n\treturn max(a,b)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_max_of3(self):
        f = "def test(a: Qint2, b: Qint2) -> Qint2:\n\treturn max(a,b,3)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_max_const(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn max(a,3)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # TODO: fix cast
    # def test_max_const2(self):
    #     f = "def test(a: Qint4) -> Qint4:\n\treturn max(a,3)"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    def test_max_tuple(self):
        f = "def test(a: Tuple[Qint2, Qint2]) -> Qint2:\n\treturn max(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_max_tuple_const(self):
        f = "def test(a: Qint2, b: Qint2) -> Qint2:\n\treturn max((a, b))"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_sum_const(self):
        f = "def test() -> Qint2:\n\treturn sum([1,2,3])"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_sum_list(self):
        f = "def test(a: Qlist[Qint2, 2]) -> Qint2:\n\treturn sum(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_sum_tuple(self):
        f = "def test(a: Tuple[Qint2, Qint2]) -> Qint2:\n\treturn sum(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_any_list(self):
        f = "def test(a: Qlist[bool, 3]) -> bool:\n\treturn any(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_any_const_list(self):
        f = "def test() -> bool:\n\treturn any([True, True, False])"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_all_list(self):
        f = "def test(a: Qlist[bool, 3]) -> bool:\n\treturn all(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_all_const_list(self):
        f = "def test() -> bool:\n\treturn all([True, True, True])"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_max_in_list(self):
        f = "def test() -> Qlist[Qint2, 3]:\n\treturn [max(0,1), max(1,2), max(2,3)]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # TODO:
    # def test_len_of_range(self):
    #     f = "def test() -> Qint4:\n\treturn len(range(4))"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    # TODO:
    # def test_range_of_len(self):
    #     f = "def test(a: Qlist[bool, 3]) -> Qint4:\n\treturn range(len(a))"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)
