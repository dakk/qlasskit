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

from qlasskit import exceptions, qlassf

from ..utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfIfThenElse(unittest.TestCase):
    def test_if_else(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\td = False\n"
            + "\tif a:\n"
            + "\t\td = not a\n"
            + "\telse:\n"
            + "\t\td = True\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_if_unbound(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\tif a:\n"
            + "\t\td = not a\n"
            + "\treturn d"
        )
        self.assertRaises(
            exceptions.UnboundException,
            lambda f: qlassf(f, to_compile=COMPILATION_ENABLED),
            (f),
        )

    def test_if(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\td = False\n"
            + "\tif a:\n"
            + "\t\td = not a\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_elif(self):
        f = (
            "def test(a: Qint2, b: bool) -> bool:\n"
            + "\td = False\n"
            + "\tif a == 0:\n"
            + "\t\td = not b\n"
            + "\telif a == 1:\n"
            + "\t\td = b\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_if_for(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\td = False\n"
            + "\ti = 0\n"
            + "\tif a:\n"
            + "\t\tfor i in range(3):\n"
            + "\t\t\td = not d\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_if_for2(self):
        f = (
            "def test(a: bool, b: bool) -> Qint[2]:\n"
            + "\td = 0\n"
            + "\tfor i in range(3):\n"
            + "\t\tif a:\n"
            + "\t\t\td += 1\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)
