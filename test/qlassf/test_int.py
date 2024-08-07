# Copyright 2023-2024 Davide Gessa

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

from parameterized import parameterized, parameterized_class
from sympy import Symbol, symbols
from sympy.logic import And, Not, Or

from qlasskit import Qint2, Qint4, exceptions, qlassf
from qlasskit.types import bin_to_bool_list

from ..utils import (
    COMPILATION_ENABLED,
    ENABLED_COMPILERS,
    compute_and_compare_results,
    inject_parameterized_compilers,
)

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


class TestQintEncoding(unittest.TestCase):
    @parameterized.expand(
        [
            (Qint4, 6, "0110"),
            (Qint4, 1, "1000"),
            (Qint4, 2, "0100"),
            (Qint4, 0, "0000"),
            (Qint4, 8, "0001"),
            (Qint4, 4, "0010"),
        ]
    )
    def test_fixed_const(self, qit, val, bin_v):
        self.assertEqual(qit.to_bin(qit(val)), bin_v)
        self.assertEqual(qit.from_bool(bin_to_bool_list(bin_v)), val)


class TestQint(unittest.TestCase):
    def test_qint2_to_amplitudes(self):
        c = Qint2(int(1)).to_amplitudes()
        self.assertEqual(c, [0.0, 1, 0.0, 0.0])
        self.assertEqual(c, Qint2(1).export("amplitudes"))

    def test_qint2_to_bin(self):
        c = Qint2(1).to_bin()
        self.assertEqual(c, "10")
        self.assertEqual(c, Qint2(1).export("binary"))


@parameterized_class(
    ("ttype_str", "ttype_size", "compiler"),
    inject_parameterized_compilers(
        [
            ("Qint[2]", 2),
            ("Qint[4]", 4),
            # ("Qint[8]", 8),
        ]
    ),
)
class TestQlassfIntParametrized_2_4_8(unittest.TestCase):
    def test_int_arg(self):
        f = f"def test(a: {self.ttype_str}) -> bool:\n\treturn a[0]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], Symbol("a.0"))
        compute_and_compare_results(self, qf)

    def test_int_arg2(self):
        f = (
            f"def test(a: {self.ttype_str}, b: bool) -> bool:\n"
            "\treturn a[1] if (a[0] and b) else a[0]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            And(Symbol("a.0"), Or(Symbol("a.1"), Not(Symbol("b")))),
            # And(Symbol("a.0"), Not(And(Symbol("b"), Not(Symbol("a.1"))))),
        )
        compute_and_compare_results(self, qf)

    def test_int_arg_unbound_index(self):
        f = f"def test(a: {self.ttype_str}) -> bool:\n\treturn a[{self.ttype_size}]"
        self.assertRaises(
            exceptions.OutOfBoundException, lambda f: qlassf(f, to_compile=False), f
        )

    def test_int_return_tuple(self):
        f = (
            f"def test(a: {self.ttype_str}) -> Tuple[{self.ttype_str}, bool]:\n"
            "\tb = a[0] and a[1]\n\treturn (a, b)"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), self.ttype_size + 1)
        compute_and_compare_results(self, qf)

    def test_int_tuple(self):
        f = (
            f"def test(a: Tuple[{self.ttype_str}, {self.ttype_str}]) -> bool:\n"
            "\treturn a[0][0] and a[1][1]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(Symbol("a.0.0"), Symbol("a.1.1")))
        compute_and_compare_results(self, qf)

    def test_int_identity(self):
        f = f"def test(a: {self.ttype_str}) -> {self.ttype_str}:\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), self.ttype_size)
        for i in range(self.ttype_size):
            self.assertEqual(qf.expressions[i][0], Symbol(f"_ret.{i}"))
            self.assertEqual(qf.expressions[i][1], Symbol(f"a.{i}"))
        compute_and_compare_results(self, qf)

    def test_int_const_compare_eq(self):
        f = f"def test(a: {self.ttype_str}) -> bool:\n\treturn a == {int(self.ttype_size/2-1)}"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)


@parameterized_class(
    ("ttype_str", "ttype_size", "compiler"),
    inject_parameterized_compilers(
        [
            ("Qint[2]", 2),
            ("Qint[4]", 4),
        ]
    ),
)
class TestQlassfIntParametrized_2_4(unittest.TestCase):
    def test_int_int_compare_eq(self):
        f = f"def test(a: {self.ttype_str}, b: {self.ttype_str}) -> bool:\n\treturn a == b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)

    def test_int_int_compare_neq(self):
        f = f"def test(a: {self.ttype_str}, b: {self.ttype_str}) -> bool:\n\treturn a != b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)

    def test_const_int_compare_gt(self):
        f = f"def test(a: {self.ttype_str}) -> bool:\n\treturn a > 1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_const_int_compare_lt(self):
        f = f"def test(a: {self.ttype_str}) -> bool:\n\treturn a < 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfInt(unittest.TestCase):
    def test_int_const(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\tc=2\n\treturn c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 2)
        self.assertEqual(qf.expressions[-2][1], False)
        self.assertEqual(qf.expressions[-1][1], True)
        compute_and_compare_results(self, qf)

    def test_int_const_compare_eq(self):
        f = "def test(a: Qint[2]) -> bool:\n\treturn a == 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(Symbol("a.1"), Not(Symbol("a.0"))))
        compute_and_compare_results(self, qf)

    def test_int_const_compare_eq_different_type(self):
        f = "def test(a: Qint[4]) -> bool:\n\treturn a == 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
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
        compute_and_compare_results(self, qf)

    def test_const_int_compare_eq_different_type(self):
        f = "def test(a: Qint[4]) -> bool:\n\treturn 2 == a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
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
        compute_and_compare_results(self, qf)

    def test_const_int_compare_neq_different_type(self):
        f = "def test(a: Qint[4]) -> bool:\n\treturn 2 != a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_int_int_compare_neq(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> bool:\n\treturn a != b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_const_int_compare_gt(self):
        f = "def test(a: Qint[4]) -> bool:\n\treturn a > 6"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        compute_and_compare_results(self, qf)

    # def test_int4_int4_compare_gt(self):
    #     f = "def test(a: Qint[4], b: Qint[4]) -> bool:\n\treturn a > b"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     # self.assertEqual(len(qf.expressions), 1)
    #     # self.assertEqual(len(qf.expressions[0][0], _ret)
    #     compute_and_compare_results(self, qf)

    def test_const_int4_compare_lt(self):
        f = "def test(a: Qint[4]) -> bool:\n\treturn a < 6"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 2)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_int_int_compare_gt(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> bool:\n\treturn a > b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_int_int_compare_lt(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> bool:\n\treturn a < b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_const_int_compare_gte(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> bool:\n\treturn a >= b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_const_int_compare_lte(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> bool:\n\treturn a <= b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-1][0], _ret)
        compute_and_compare_results(self, qf)

    def test_ite_return_qint(self):
        f = "def test(a: bool, b: Qint[2], c: Qint[2]) -> Qint[2]:\n\treturn b if a else c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(qf.expressions[-2][0], Symbol("_ret.0"))
        self.assertEqual(qf.expressions[-1][0], Symbol("_ret.1"))
        compute_and_compare_results(self, qf)

    def test_composed_comparators(self):
        f = "def f_comp(n: Qint[4]) -> bool: return n > 3 or n == 7"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    @parameterized.expand(
        [
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_shift_left(self, v):
        f = f"def test(n: Qint[4]) -> Qint[4]: return n << {v}"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    @parameterized.expand(
        [
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_shift_right(self, v):
        f = f"def test(n: Qint[2]) -> Qint[4]: return n >> {v}"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # Our Qint are unsigned
    # def test_invert_bitwise_not(self):
    #     f = "def test(n: Qint[4]) -> bool: return ~n"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)


# TODO: parameterize
@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfIntAdd(unittest.TestCase):
    def test_add_tuple(self):
        f = "def test(a: Tuple[Qint[2], Qint[2]]) -> Qint[2]: return a[0] + a[1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_add(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> Qint[2]: return a + b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_add_const(self):
        f = "def test(a: Qint[2]) -> Qint[2]: return a + 1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_add_const2(self):
        f = "def test() -> Qint[4]: return Qint4(3) + 3"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_add_const3(self):
        f = (
            "def test(a: Qint[2], b: Qint[2]) -> Qint[4]: "
            "return Qint4(3) + a if a == 3 else Qint4(1) + b"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_add_const4(self):
        f = "def test(a: Qint[2]) -> Qint[2]: return a + 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)


@parameterized_class(
    ("val", "compiler"),
    inject_parameterized_compilers(
        [
            (1,),
            (2,),
            (4,),
            (8,),
            (16,),
        ]
    ),
)
class TestQlassfIntMod(unittest.TestCase):
    def test_mod_const(self):
        f = f"def test(a: Qint[4]) -> Qint[4]: return a % {self.val}"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_mod_const_in_var(self):
        f = f"def test(a: Qint[4]) -> Qint[4]:\n\tb = {self.val}\n\treturn a % b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfIntSub(unittest.TestCase):
    def test_sub_const(self):
        f = "def test(a: Qint[2]) -> Qint[2]: return a - 1"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_sub_const2(self):
        f = "def test(a: Qint[2]) -> Qint[2]: return a - 3"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_sub_const3(self):
        f = "def test(a: Qint[4]) -> Qint[4]: return a - 8"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)


@parameterized_class(
    ("ttype_str", "ttype_size", "compiler"),
    inject_parameterized_compilers(
        [
            ("Qint[2]", 2),
            ("Qint[4]", 4),
        ]
    ),
)
class TestQlassfIntBitwise(unittest.TestCase):
    def test_bitwise_and(self):
        f = (
            f"def test(a: {self.ttype_str}, b: {self.ttype_str}) -> {self.ttype_str}:\n"
            "\treturn a & b"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_bitwise_or(self):
        f = (
            f"def test(a: {self.ttype_str}, b: {self.ttype_str}) -> {self.ttype_str}:\n"
            "\treturn a | b"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_bitwise_xor(self):
        f = (
            f"def test(a: {self.ttype_str}, b: {self.ttype_str}) -> {self.ttype_str}:\n"
            "\treturn a ^ b"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfIntReassign(unittest.TestCase):
    def test_reassign_newvar(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\tb = 0\n\tb = a + 1\n\treturn b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_reassign_arg(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\ta = a + 1\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_aug_reassign_newvar(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\tb = a\n\tb += 1\n\treturn b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_aug_reassign_arg(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\ta += 1\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfIntMul(unittest.TestCase):
    def test_mul(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> Qint[4]: return a * b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_mul_and_sum(self):
        f = "def test(a: Qint[2], b: Qint[2], c: Qint[2]) -> Qint[2]: return a * b + c"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_mult_multconst(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> Qint[4]:\n\treturn (a * b) * 5"
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_mul_const(self):
        f = "def test(a: Qint[2], b: Qint[4]) -> Qint[4]:\n\treturn (a * 3) + b"
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_mul4(self):
        f = "def test(a: Qint[4], b: Qint[4]) -> Qint[8]: return a * b"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_mul5(self):
        f = "def test(a: Qint[3], b: Qint[3]) -> bool: return 3*2==6"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
        self.assertEqual(qf.expressions[0][1], True)


@parameterized_class(
    ("ttype_i", "ttype_o", "const", "compiler"),
    inject_parameterized_compilers(
        [
            (4, 6, 2),
            (4, 6, 4),
            (4, 6, 6),
            (6, 8, 6),
            (6, 8, 8),
            (6, 8, 10),
        ]
    ),
)
class TestQlassfIntMulByConst(unittest.TestCase):
    def test_mul(self):
        f = f"def test(a: Qint[{self.ttype_i}]) -> Qint[{self.ttype_o}]: return a * {self.const}"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfIntPow(unittest.TestCase):
    def test_pow_const(self):
        f = "def test(a: Qint[4]) -> Qint[8]: return a ** 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_pow_const2(self):
        f = "def test(a: Qint[4]) -> Qint[16]: return a ** 3"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_pow_const3(self):
        f = "def test(a: Qint[2]) -> Qint[16]: return a ** 4"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_pow_zero(self):
        f = "def test(a: Qint[4]) -> Qint[4]: return a ** 0"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)
