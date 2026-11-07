# Copyright (C) 2023-2026 Davide Gessa
# This file is part of Qlasskit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
