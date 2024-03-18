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

from parameterized import parameterized_class
from sympy import Symbol
from sympy.logic import And, Not

from qlasskit import Qchar, qlassf

from ..utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQchar(unittest.TestCase):
    def test_qchar_to_bin_and_from_bool(self):
        c = Qchar("a").to_bin()
        self.assertEqual(c, "01100001"[::-1])
        self.assertEqual(c, Qchar("a").export("binary"))
        self.assertEqual(
            Qchar.from_bool(
                [False, True, True, False, False, False, False, True][::-1]
            ),
            "a",
        )

    def test_char_arg_eq(self):
        f = "def test(a: Qchar) -> bool:\n\treturn a == 'a'"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], Symbol("_ret"))
        a = [Symbol(f"a.{i}") for i in range(8)]
        self.assertEqual(
            qf.expressions[0][1],
            And(
                a[0], a[5], a[6], Not(a[1]), Not(a[2]), Not(a[3]), Not(a[4]), Not(a[7])
            ),
        )
        compute_and_compare_results(self, qf)

    def test_char_arg_neq(self):
        f = "def test(a: Qchar) -> bool:\n\treturn a != 'a'"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], Symbol("_ret"))
        a = [Symbol(f"a.{i}") for i in range(8)]
        self.assertEqual(
            qf.expressions[0][1],
            Not(
                And(
                    a[0],
                    a[5],
                    a[6],
                    Not(a[1]),
                    Not(a[2]),
                    Not(a[3]),
                    Not(a[4]),
                    Not(a[7]),
                )
            ),
        )
        compute_and_compare_results(self, qf)

    def test_char_return(self):
        f = "def test(a: Qchar) -> Qchar:\n\treturn 'z' if a == 'a' else 'a'"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_char_return2(self):
        f = "def test(a: Qchar) -> Qchar:\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_char_return_tuple(self):
        f = (
            "def test(a: Qchar) -> Tuple[Qchar, bool]:\n"
            "\tb = a == 'z'\n\treturn (a, b)"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 9)
        compute_and_compare_results(self, qf)

    def test_char_ord(self):
        f = "def test(a: Qchar) -> bool:\n\treturn ord(a) == 97"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_char_chr(self):
        f = "def test(a: Qchar) -> bool:\n\treturn a == chr(97)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
