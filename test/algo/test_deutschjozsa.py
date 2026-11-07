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

from qlasskit import qlassf
from qlasskit.algorithms import DeutschJozsa

from ..utils import ENABLED_COMPILERS, qiskit_measure_and_count


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestAlgoDeutschJozsa(unittest.TestCase):
    def test_deutschjozsa_balanced(self):
        f = """
def hash(k: Qint2) -> bool:
    return k[0] ^ k[1]
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = DeutschJozsa(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable["Balanced"], 1024)

    def test_deutschjozsa_balanced2(self):
        f = """
def hash(k: bool) -> bool:
    return k
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = DeutschJozsa(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable["Balanced"], 1024)

    def test_deutschjozsa_constant(self):
        f = """
def hash(k: Qint2) -> bool:
    return False
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = DeutschJozsa(qf)

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)
        self.assertEqual(counts_readable["Constant"], 1024)
