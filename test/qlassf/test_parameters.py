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

from sympy import Symbol

from qlasskit import qlassf

from ..utils import COMPILATION_ENABLED, compute_and_compare_results


class TestQlassfParameters(unittest.TestCase):
    def test_bind_bool(self):
        uqf = qlassf(
            "def test(c: Parameter[bool], a: bool) -> bool: return a and c",
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=True)
        self.assertEqual(qf.expressions[0][1], Symbol("a"))
        compute_and_compare_results(self, qf)

        qf = uqf.bind(c=False)
        self.assertEqual(qf.expressions[0][1], False)
        compute_and_compare_results(self, qf)

    def test_bind_qint2(self):
        uqf = qlassf(
            "def test(c: Parameter[Qint[2]], a: bool) -> Qint[2]: return c+1 if a else c",
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=1)
        compute_and_compare_results(self, qf)

    def test_bind_multiple_qint2(self):
        uqf = qlassf(
            (
                "def test(c: Parameter[Qint[2]], d: Parameter[Qint[2]], a: bool) -> Qint[2]: "
                "return c+d if a else c+1"
            ),
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=1, d=2)
        compute_and_compare_results(self, qf)

    def test_bind_list(self):
        uqf = qlassf(
            "def test(c: Parameter[Qlist[2, bool]]) -> bool: return c[0] and c[1]",
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=[True, True])
        compute_and_compare_results(self, qf)

    def test_bind_tuple(self):
        uqf = qlassf(
            (
                "def test(c: Parameter[Tuple[bool, Qint[2]]]) -> Qint[2]:"
                "return c[1] if c[0] else c[1]+1"
            ),
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=(True, 2))
        compute_and_compare_results(self, qf)
