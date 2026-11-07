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
from typing import Tuple

from parameterized import parameterized
from sympy import Symbol
from sympy.logic import And

from qlasskit import Qint, Qint2, Qint4, Qlist, Qtype
from qlasskit.types import format_outcome, interpret_as_qtype


class TestTypes_format_outcome(unittest.TestCase):
    def test_format_outcome_str(self):
        out = "1011"
        self.assertEqual(format_outcome(out), [True, False, True, True])

    def test_format_outcome_str_with_out_len(self):
        out = "1011"
        self.assertEqual(format_outcome(out, 5), [True, False, True, True, False])

    def test_format_outcome_int(self):
        out = 15
        self.assertEqual(format_outcome(out), [True, True, True, True])

    def test_format_outcome_int_with_out_len(self):
        out = 15
        self.assertEqual(format_outcome(out, 5), [True, True, True, True, False])

    def test_format_outcome_bool(self):
        out = [True, True]
        self.assertEqual(format_outcome(out), [True, True])

    def test_format_outcome_bool_with_out_len(self):
        out = [True, True]
        self.assertEqual(format_outcome(out, 3), [True, True, False])


class TestTypes_interpret_as_type(unittest.TestCase):
    def test_interpret_bool(self):
        _out = interpret_as_qtype([False, True], bool, 1)
        self.assertEqual(_out, True)

    def test_interpret_qint2(self):
        _out = interpret_as_qtype([False, True], Qint2, 2)
        self.assertEqual(_out, 1)

    def test_interpret_qint4(self):
        _out = interpret_as_qtype([True, True, True, False], Qint4, 4)
        self.assertEqual(_out, 14)

    def test_interpret_qlist_bool_3(self):
        _out = list(interpret_as_qtype([True, True, False], Qlist[bool, 3], 3))
        self.assertEqual(_out, [False, True, True])

    def test_interpret_tuple_bool(self):
        _out = interpret_as_qtype([True, True, False], Tuple[bool, bool, bool], 3)
        self.assertEqual(_out, (False, True, True))


class TestTypes_Qtype(unittest.TestCase):
    @parameterized.expand(
        [
            ((bool, [False]), True),
            ((bool, [Symbol("a")]), False),
            ((bool, [And(False, False)]), True),
            ((Qint[2], [False, False]), True),
            ((Qint[2], [False, Symbol("a")]), False),
        ]
    )
    def test_is_const(self, tval, res):
        self.assertEqual(Qtype.is_const(tval), res)

    @parameterized.expand(
        [((Qint2, [True]), [True, False]), ((Qint2, [False, True]), [False, True])]
    )
    def test_fill(self, tval, res):
        self.assertEqual(tval[0].fill(tval)[1], res)

    @parameterized.expand(
        [
            ((Qint2, [True, False, False]), [True, False]),
            ((Qint2, [False, True]), [False, True]),
        ]
    )
    def test_crop(self, tval, res):
        self.assertEqual(tval[0].crop(tval)[1], res)
