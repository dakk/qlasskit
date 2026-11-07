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

from parameterized import parameterized_class
from sympy import And, Not, Symbol

from qlasskit import qlassf
from qlasskit.algorithms import ConstantOracleException, QAlgorithm, oraclize
from qlasskit.types import interpret_as_qtype

from ..utils import ENABLED_COMPILERS


class QT(QAlgorithm):
    def __init__(self, tt, ll):
        self.tt = tt
        self.ll = ll

    def decode_output(self, oc):
        return interpret_as_qtype(oc, self.tt, self.ll)


class TestAlgo_interpret_counts(unittest.TestCase):
    def test_interpret_counts(self):
        q = QT(bool, 1)
        c = q.decode_counts({"010": 3, "110": 2, "111": 1})
        self.assertEqual(c, {False: 5, True: 1})

    def test_interpret_counts2(self):
        q = QT(Tuple[bool, bool], 2)
        c = q.decode_counts({"010": 3, "110": 2, "111": 1})
        self.assertEqual(c, {(False, True): 5, (True, True): 1})


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestAlgo_oraclize(unittest.TestCase):
    def test_constant_oracle(self):
        q = qlassf("def test(a: bool) -> bool: return True", compiler=self.compiler)
        self.assertRaises(ConstantOracleException, lambda x: oraclize(q, True), True)

    def test_oracle_identity(self):
        q = qlassf("def test(a: bool) -> bool: return a", compiler=self.compiler)
        orac = oraclize(q, True)
        orac.compile(compiler=self.compiler)
        self.assertEqual(orac.name, "oracle")
        self.assertEqual(orac.expressions, [(Symbol("_ret"), Symbol("v"))])

    def test_oracle_tuple(self):
        q = qlassf(
            "def test(a: Tuple[bool, bool]) -> bool: return a[0] and a[1]",
            compiler=self.compiler,
        )
        orac = oraclize(q, True)
        orac.compile(compiler=self.compiler)
        self.assertEqual(
            orac.expressions, [(Symbol("_ret"), And(Symbol("v.0"), Symbol("v.1")))]
        )

    def test_oracle_qtype(self):
        q = qlassf("def test(a: Qint2) -> Qint2: return a", compiler=self.compiler)
        orac = oraclize(q, 1)
        orac.compile(compiler=self.compiler)
        self.assertEqual(
            orac.expressions, [(Symbol("_ret"), And(Symbol("v.0"), Not(Symbol("v.1"))))]
        )
