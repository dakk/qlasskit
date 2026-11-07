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
from sympy import Symbol, symbols

from qlasskit import qlassf

from ..utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestForLoop(unittest.TestCase):
    def test_for_1it(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\tfor x in range(1):\n\t\ta += 1\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_4it(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\tfor x in range(4):\n\t\ta += 1\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_3it(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\tfor i in range(3):\n\t\ta += i\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_nit_bool(self):
        f = "def test(a: bool) -> bool:\n\tfor i in range(4):\n\t\ta = not a\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_nit_bool_many(self):
        f = "def test(a: bool) -> bool:\n\tfor i in range(15):\n\t\ta = not a\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # def test_for_nit_tbool_many(self):
    #     f = (
    #       "def test(a: Tuple[bool,bool]) -> Tuple[bool,bool]:\n\tfor i in range(32):\n"
    #       "\t\ta[0] = not a[0]\n\t\ta[1] = not a[1]\n\treturn a"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    def test_for_cond(self):
        f = (
            "def test(a: Qint[2], b: bool) -> Qint[2]:\n\tfor i in range(2):\n"
            "\t\ta += (i if b else 1)\n\treturn a"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_sum(self):
        f = (
            "def hash(k: Qint[4]) -> bool:\n\tz = 1\n\tfor i in range(3):\n"
            "\t\tz += i\n\treturn z == 3"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_sum2(self):
        f = (
            "def hash(k: Qlist[bool, 4]) -> bool:\n\th = True\n\tfor i in range(len(k)):"
            "\n\t\th = h and k[i]\n\treturn h"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
