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

from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, compare_circuit_truth_table

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


class TestQlassfInt(unittest.TestCase):
    def test_int_arg(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a[0]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], Symbol("a.0"))
        # compare_circuit_truth_table(self, qf)

    def test_int_arg2(self):
        f = "def test(a: Qint2, b: bool) -> bool:\n\treturn True if a[0] and b else a[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1], ITE(And(Symbol("a.0"), b), True, Symbol("a.1"))
        )
        compare_circuit_truth_table(self, qf)

    def test_int_arg_unbound_index(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a[5]"
        self.assertRaises(
            exceptions.OutOfBoundException, lambda f: qlassf(f, to_compile=False), f
        )

    def test_int_tuple(self):
        f = "def test(a: Tuple[Qint2, Qint2]) -> bool:\n\treturn a[0][0] and a[1][1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(Symbol("a.0.0"), Symbol("a.1.1")))
        compare_circuit_truth_table(self, qf)

    def test_int_identity(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 2)
        self.assertEqual(qf.expressions[0][0], Symbol("_ret.0"))
        self.assertEqual(qf.expressions[0][1], Symbol("a.0"))
        self.assertEqual(qf.expressions[1][0], Symbol("_ret.1"))
        self.assertEqual(qf.expressions[1][1], Symbol("a.1"))
        compare_circuit_truth_table(self, qf)

    # TODO: need consts
    # def test_int_const(self):
    #     f = "def test(a: Qint2) -> Qint2:\n\tc=1\n\treturn a"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED)

    # TODO: need comparators
    # def test_int_compare(self):
    #     f = "def test(a: Qint2) -> bool:\n\treturn a == 1"
    #     qf = qlassf(f, to_compile=False)
    #     self.assertEqual(len(qf.expressions), 1)
    #     self.assertEqual(qf.expressions[0][0], _ret)
    #     self.assertEqual(qf.expressions[0][1], a)

    # def test9(a: Int8) -> bool:
    #     return a == 42

    # Raise costant return
    # def test10() -> Int8:
    #     return 42

    # def test11(a: Int2) -> Int2:
    #     return a + 1

    # def test12(a: bool) -> Int8:
    #     return 42 if a else 38
