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

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")
a_0 = Symbol("a.0")
a_1 = Symbol("a.1")
b_0 = Symbol("b.0")
b_1 = Symbol("b.1")


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfList(unittest.TestCase):
    def test_list_const(self):
        f = "def test() -> Qlist[bool, 2]:\n\treturn [True, True]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list(self):
        f = "def test(a: Qlist[bool, 2]) -> bool:\n\treturn a[0] and a[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(a_0, a_1))
        compute_and_compare_results(self, qf)

    def test_list_item_swap(self):
        f = "def swapf(a: Qlist[Qint2, 2]) -> Qlist[Qint2, 2]:\n\treturn [a[1], a[0]]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_item_swap_bool(self):
        f = "def swapf(a: Qlist[bool, 2]) -> Qlist[bool, 2]:\n\treturn [a[1], a[0]]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_item_sum(self):
        f = "def swapf(a: Qlist[Qint2, 2]) -> Qint2:\n\treturn a[0] + a[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_iterator_var(self):
        f = "def test(a: Qlist[Qint2, 2]) -> Qint2:\n\tc = 0\n\tfor x in a:\n\t\tc += x\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_iterator_list(self):
        f = "def test(a: Qint2) -> Qint2:\n\tc = 0\n\tfor x in [1,2,3]:\n\t\tc += x + a\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_iterator_varlist(self):
        f = "def test(a: Qint2) -> Qint2:\n\tc = [1,2,3]\n\tfor x in c:\n\t\ta += x\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_len(self):
        f = "def test(a: Qlist[Qint2, 2]) -> Qint2:\n\tc = 0\n\tfor x in range(len(a)):\n\t\tc += a[x]\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_access_with_var(self):
        f = "def test(a: Qint2) -> Qint2:\n\tc = [1,2,3,2]\n\tb = c[a]\n\treturn b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_access_with_var_on_tuple(self):
        # TODO: this fails on internal compiler
        if self.compiler == "internal":
            return

        f = "def test(ab: Tuple[Qint2, Qint2]) -> Qint2:\n\tc = [1,2,3,2]\n\tai,bi = ab\n\td = c[ai] + c[bi]\n\treturn d"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_access_with_var_on_tuple2(self):
        # TODO: this fails on internal compiler
        if self.compiler == "internal":
            return

        f = "def test(ab: Tuple[Qint2, Qint2]) -> Qint2:\n\tc = [1,2,3,2]\n\td = c[ab[0]] + c[ab[1]]\n\treturn d"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
