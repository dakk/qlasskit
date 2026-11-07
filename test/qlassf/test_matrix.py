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
a_0 = Symbol("a.0")
a_1 = Symbol("a.1")
b_0 = Symbol("b.0")
b_1 = Symbol("b.1")


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfMatrix(unittest.TestCase):
    def test_matrix_const_2x2(self):
        f = "def test() -> Qmatrix[bool, 2, 2]:\n\treturn [[True, True], [True, False]]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_const_2x3(self):
        f = "def test() -> Qmatrix[bool, 2, 3]:\n\treturn [[True, True, True], [True, False, True]]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_const_3x2(self):
        f = (
            "def test() -> Qmatrix[bool, 3, 2]:\n\treturn [[True, True], [True, False], "
            "[True, False]]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_access(self):
        f = "def test(a: Qmatrix[bool, 2, 2]) -> bool:\n\treturn a[0][1]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], Symbol("a.0.1"))
        compute_and_compare_results(self, qf)

    def test_matrix_iterator_var(self):
        f = (
            "def test(a: Qmatrix[Qint[2], 2, 2]) -> Qint[2]:\n\tc = 0\n\tfor x in a:\n"
            "\t\tfor y in x:\n\t\t\tc += y\n\treturn c"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_iterator_list(self):
        f = (
            "def test(a: Qint[2]) -> Qint[2]:\n\tc = 0\n\tfor x in [[1,2],[3,4]]:\n"
            "\t\tfor y in x:\n\t\t\tc += y + a\n\treturn c"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_iterator_varlist(self):
        f = (
            "def test(a: Qint[2]) -> Qint[2]:\n\tc = [[1,2],[3,4]]\n\tfor x in c:\n"
            "\t\tfor y in x:\n\t\t\ta += y\n\treturn a"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_len(self):
        f = (
            "def test(a: Qmatrix[Qint[2], 2, 2]) -> Qint[2]:\n\tc = 0\n"
            "\tfor x in range(len(a)):\n\t\tc += a[x][0]\n\treturn c"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_access2(self):
        f = (
            "def test(a: Qmatrix[Qint[2], 2, 2]) -> Qint[2]:\n\ti = 0\n"
            "\tj = i + 1\n\treturn a[i][j]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_access3(self):
        f = (
            "def test(a: Qmatrix[Qint[2], 2, 2], i: Qint[2], j: Qint[2]) -> Qint[2]:\n"
            "\treturn a[i][j]"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_matrix_access_with_var(self):
        f = (
            "def test(a: Qint[2]) -> Qint[4]:\n\tc = [[1,2,7,8],[3,4,8,8],[5,6,9,1],[1,2,7,8]]\n"
            "\tb = c[a][a]\n\treturn b"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_access_with_var_on_tuple(self):
        f = (
            "def test(ab: Tuple[Qint[2], Qint[2]]) -> Qint[2]:\n\tc = [1,2,3,2]\n\tai,bi = ab\n"
            "\td = c[ai] + c[bi]\n\treturn d"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_list_access_with_var_on_tuple2(self):
        f = (
            "def test(ab: Tuple[Qint[2], Qint[2]]) -> Qint[2]:\n\tc = [1,2,3,2]\n"
            "\td = c[ab[0]] + c[ab[1]]\n\treturn d"
        )
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
