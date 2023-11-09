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
from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results

a, b, c, d, e, g, h = symbols("a,b,c,d,e,g,h")
_ret = Symbol("_ret")


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfBoolean(unittest.TestCase):
    def test_unbound(self):
        f = "def test() -> bool:\n\treturn a"
        self.assertRaises(
            exceptions.UnboundException, lambda f: qlassf(f, to_compile=False), f
        )

    def test_no_return_type(self):
        f = "def test(a: bool):\n\treturn a"
        self.assertRaises(
            exceptions.NoReturnTypeException, lambda f: qlassf(f, to_compile=False), f
        )

    def test_bool_const(self):
        f = "def test(a: bool) -> bool:\n\tc=True\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], True)
        compute_and_compare_results(self, qf)

    def test_arg_identity(self):
        ex = a
        f = "def test(a: bool) -> bool:\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_not_arg(self):
        ex = Not(a)
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_and(self):
        ex = And(Not(a), b)
        f = "def test(a: bool, b: bool) -> bool:\n\treturn not a and b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_bool_eq(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a == b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)

    def test_bool_neq(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a != b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)

    def test_or_not(self):
        ex = Not(And(a, Not(b)))
        f = "def test(a: bool, b: bool) -> bool:\n\treturn not a or b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_multiple_arg(self):
        ex = And(a, And(Not(b), c))
        f = "def test(a: bool, b: bool, c: bool) -> bool:\n\treturn a and (not b) and c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_multiple_arg2(self):
        # ex = And(a, Not(b))
        f = "def test(a: bool, b: bool, c: bool) -> bool:\n\treturn a and (not b) and (a or c)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        # self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_ifexp(self):
        ex = ITE(a, true, false)
        f = "def test(a: bool) -> bool:\n\treturn True if a else False"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_ifexp2(self):
        ex = ITE(And(a, And(Not(b), c)), true, false)
        f = "def test(a: bool, b: bool, c: bool) -> bool:\n\treturn True if a and (not b) and c else False"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)
        compute_and_compare_results(self, qf)

    def test_ifexp3(self):
        exp = And(a, Not(And(b, c)))
        f = (
            "def test(a: bool, b: bool, c: bool) -> bool:\n"
            + "\treturn (c and not b) if a and ((not b) and c) else (a and not c)"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], exp)
        compute_and_compare_results(self, qf)

    def test_assign(self):
        f = "def test(a: bool, b: bool) -> bool:\n\tc = a and b\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(a, b))
        compute_and_compare_results(self, qf)

    def test_assign2(self):
        f = (
            "def test(a: bool, b: bool, c: bool) -> bool:\n"
            + "\td = a and (not b) and c\n"
            + "\treturn True if d else False"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][1], And(a, And(Not(b), c)))
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)

    def test_assign3(self):
        f = (
            "def test(a: bool, b: bool, c: bool) -> bool:\n"
            + "\td = a and (not b) and c\n"
            + "\te = a and b and c\n"
            + "\tg = (not a) and b and c\n"
            + "\th = (not a) and b and (not c)\n"
            + "\treturn g if d and e else h"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][1], And(b, Not(a), Not(c)))
        compute_and_compare_results(self, qf)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfBoolBitwise(unittest.TestCase):
    def test_bitwise_and(self):
        f = f"def test(a: bool, b: bool) -> bool:\n\treturn a & b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_bitwise_or(self):
        f = f"def test(a: bool, b: bool) -> bool:\n\treturn a | b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_bitwise_xor(self):
        f = f"def test(a: bool, b: bool) -> bool:\n\treturn a ^ b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
