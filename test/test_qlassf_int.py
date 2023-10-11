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

import pytest
from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, Xor, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf  # Qint2

from .utils import COMPILATION_ENABLED, compare_circuit_truth_table

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


# @pytest.mark.parametrize("qint", [Qint2])
class TestQlassfInt(unittest.TestCase):
    def test_int_arg(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a[0]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], Symbol("a.0"))
        # compare_circuit_truth_table(self, qf)

    def test_int_arg2(self):
        f = "def test(a: Qint2, b: bool) -> bool:\n\treturn True if (a[0] and b) else a[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1], ITE(And(Symbol("a.0"), b), True, Symbol("a.1"))
        )
        compare_circuit_truth_table(self, qf)

    def test_const_return(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn 1"
        self.assertRaises(
            exceptions.ConstantReturnException, lambda f: qlassf(f, to_compile=False), f
        )

    def test_int_arg_unbound_index(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a[5]"
        self.assertRaises(
            exceptions.OutOfBoundException, lambda f: qlassf(f, to_compile=False), f
        )

    def test_int_return_tuple(self):
        f = "def test(a: Qint2) -> Tuple[Qint2, bool]:\n\tb = a[0] and a[1]\n\treturn (a, b)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 4)
        compare_circuit_truth_table(self, qf)

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

    def test_int_const_compare_eq(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a == 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(Symbol("a.1"), Not(Symbol("a.0"))))
        compare_circuit_truth_table(self, qf)

    def test_int_const_compare_eq_different_type(self):
        f = "def test(a: Qint4) -> bool:\n\treturn a == 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            And(
                Symbol("a.1"),
                Not(Symbol("a.0")),
                Not(Symbol("a.2")),
                Not(Symbol("a.3")),
            ),
        )
        compare_circuit_truth_table(self, qf)

    def test_const_int_compare_eq_different_type(self):
        f = "def test(a: Qint4) -> bool:\n\treturn 2 == a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            And(
                Symbol("a.1"),
                Not(Symbol("a.0")),
                Not(Symbol("a.2")),
                Not(Symbol("a.3")),
            ),
        )
        compare_circuit_truth_table(self, qf)

    def test_const_int_compare_neq_different_type(self):
        f = "def test(a: Qint4) -> bool:\n\treturn 2 != a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            Or(
                Not(Symbol("a.1")),
                Symbol("a.0"),
                Symbol("a.2"),
                Symbol("a.3"),
            ),
        )
        compare_circuit_truth_table(self, qf)

    def test_int_int_compare_eq(self):
        f = "def test(a: Qint2, b: Qint2) -> bool:\n\treturn a == b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            And(
                Not(Xor(Symbol("a.0"), Symbol("b.0"))),
                Not(Xor(Symbol("a.1"), Symbol("b.1"))),
            ),
        )
        compare_circuit_truth_table(self, qf)

    def test_int_int_compare_neq(self):
        f = "def test(a: Qint2, b: Qint2) -> bool:\n\treturn a != b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            Or(
                Xor(Symbol("a.0"), Symbol("b.0")),
                Xor(Symbol("a.1"), Symbol("b.1")),
            ),
        )
        compare_circuit_truth_table(self, qf)

    def test_const_int_compare_gt(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a > 1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compare_circuit_truth_table(self, qf)

    def test_const_int4_compare_gt(self):
        f = "def test(a: Qint4) -> bool:\n\treturn a > 3"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compare_circuit_truth_table(self, qf)

    def test_const_int_compare_lt(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a < 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compare_circuit_truth_table(self, qf)

    # def test_const_int4_compare_lt(self):
    #     f = "def test(a: Qint4) -> bool:\n\treturn a < 6"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED)
    #     self.assertEqual(len(qf.expressions), 1)
    #     self.assertEqual(qf.expressions[0][0], _ret)
    #     compare_circuit_truth_table(self, qf)

    def test_int_int_compare_gt(self):
        f = "def test(a: Qint2, b: Qint2) -> bool:\n\treturn a > b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compare_circuit_truth_table(self, qf)

    def test_int_int_compare_lt(self):
        f = "def test(a: Qint2, b: Qint2) -> bool:\n\treturn a < b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compare_circuit_truth_table(self, qf)

    # def test_const_int_compare_gte(self):
    #     f = "def test(a: Qint2, b: Qint2) -> bool:\n\treturn a >= b"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED)
    #     self.assertEqual(len(qf.expressions), 1)
    #     self.assertEqual(qf.expressions[0][0], _ret)
    #     compare_circuit_truth_table(self, qf)

    # def test_const_int_compare_lte(self):
    #     f = "def test(a: Qint2, b: Qint2) -> bool:\n\treturn a <= b"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED)
    #     self.assertEqual(len(qf.expressions), 1)
    #     self.assertEqual(qf.expressions[0][0], _ret)
    #     compare_circuit_truth_table(self, qf)

    def test_ite_return_qint(self):
        f = "def test(a: bool, b: Qint2, c: Qint2) -> Qint2:\n\treturn b if a else c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        self.assertEqual(len(qf.expressions), 2)
        self.assertEqual(qf.expressions[0][0], Symbol("_ret.0"))
        self.assertEqual(qf.expressions[0][1], ITE(a, Symbol("b.0"), Symbol("c.0")))
        self.assertEqual(qf.expressions[1][0], Symbol("_ret.1"))
        self.assertEqual(qf.expressions[1][1], ITE(a, Symbol("b.1"), Symbol("c.1")))
        # compare_circuit_truth_table(self, qf) TODO: fix

    # def test(a: Qint2) -> Qint2:
    #     return a + 1
    # def test(a: Qint2, b: Qint2) -> Qint2:
    #     return a + b
