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
from sympy import Symbol, symbols, sympify
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
class TestQlassfTuple(unittest.TestCase):
    def test_tuple_const(self):
        f = "def test() -> Tuple[bool, bool]:\n\treturn (True, True)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_arg(self):
        f = "def test(a: Tuple[bool, bool]) -> bool:\n\treturn a[0] and a[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(a_0, a_1))
        compute_and_compare_results(self, qf)

    def test_tuple_item_swap(self):
        f = "def swapf(a: Tuple[Qint2, Qint2]) -> Tuple[Qint2, Qint2]:\n\treturn (a[1], a[0])"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_ite(self):
        f = "def test(b: bool, a: Tuple[bool, bool]) -> Tuple[bool,bool]:\n\treturn (a[1],a[0]) if b else a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_arg_assign(self):
        f = (
            "def test(a: Tuple[bool, bool]) -> bool:\n"
            + "\tb = a[0]\n"
            + "\tc = a[1]\n"
            + "\treturn b and c"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[-1][0], _ret)
        self.assertEqual(qf.expressions[-1][1], And(Symbol("a.0"), Symbol("a.1")))
        compute_and_compare_results(self, qf)

    def test_tuple_of_tuple_arg(self):
        f = "def test(a: Tuple[Tuple[bool, bool], bool]) -> bool:\n\treturn a[0][0] and a[0][1] and a[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1], And(Symbol("a.0.0"), And(Symbol("a.0.1"), a_1))
        )
        compute_and_compare_results(self, qf)

    def test_tuple_of_tuple_of_tuple_arg(self):
        f = (
            "def test(a: Tuple[Tuple[Tuple[bool, bool], bool], bool]) -> bool:\n"
            + "\treturn a[0][0][0] and a[0][0][1] and a[0][1] and a[1]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            And(Symbol("a.0.0.0"), And(Symbol("a.0.0.1"), And(Symbol("a.0.1"), a_1))),
        )
        compute_and_compare_results(self, qf)

    def test_tuple_assign(self):
        f = "def test(a: Tuple[bool, bool]) -> bool:\n\tb = (a[1],a[0])\n\treturn b[0] and b[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(a_0, a_1))
        compute_and_compare_results(self, qf)

    def test_tuple_assign2(self):
        f = (
            "def test(a: Tuple[Tuple[bool, bool], bool]) -> bool:\n"
            + "\tb = (a[0][1],a[0][0],a[1])\n"
            + "\treturn b[0] and b[1] and b[2]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1], And(Symbol("a.0.0"), Symbol("a.0.1"), Symbol("a.1"))
        )
        compute_and_compare_results(self, qf)

    def test_tuple_assign3(self):
        f = (
            "def test(a: Tuple[Tuple[bool, bool], bool]) -> bool:\n"
            + "\tb = (a[0][1],(a[0][0],a[1]))\n"
            + "\treturn b[0] and b[1][0] and b[1][1]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1], And(Symbol("a.0.0"), Symbol("a.0.1"), Symbol("a.1"))
        )
        compute_and_compare_results(self, qf)

    def test_multi_assign(self):
        f = "def test(a: bool) -> bool:\n\tc, d = a, not a\n\treturn c and d"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_multi_assign2(self):
        f = "def test() -> Qint4:\n\tc, d = 1, 2\n\treturn c+d"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_multi_assign3(self):
        f = "def test() -> Qint4:\n\tc, d, e = 1, 2, 0xa\n\treturn c+d+e"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_result(self):
        f = "def test(a: bool, b: bool) -> Tuple[bool,bool]:\n\treturn a,b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 2)
        self.assertEqual(qf.expressions[0][0], Symbol("_ret.0"))
        self.assertEqual(qf.expressions[0][1], a)
        self.assertEqual(qf.expressions[1][0], Symbol("_ret.1"))
        self.assertEqual(qf.expressions[1][1], b)
        compute_and_compare_results(self, qf)

    def test_tuple_compare(self):
        f = "def test(a: Tuple[bool, bool], b: Tuple[bool, bool]) -> bool:\n\treturn a == b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_int_compare(self):
        f = "def test(a: Tuple[Qint2, Qint2], b: Tuple[Qint2, Qint2]) -> bool:\n\treturn a == b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_iterator_var(self):
        f = "def test(a: Tuple[Qint2, Qint2]) -> Qint2:\n\tc = 0\n\tfor x in a:\n\t\tc += x\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_iterator_tuple(self):
        f = "def test(a: Qint2) -> Qint2:\n\tc = 0\n\tfor x in (1,2,3):\n\t\tc += x + a\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_tuple_iterator_vartuple(self):
        f = "def test(a: Qint2) -> Qint2:\n\tc = (1,2,3)\n\tfor x in c:\n\t\ta += x\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
