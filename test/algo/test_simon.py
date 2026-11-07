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
from qlasskit.algorithms import Simon

from ..utils import ENABLED_COMPILERS, qiskit_measure_and_count


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestAlgoSimon(unittest.TestCase):
    def test_simon(self):
        f = """
def hash(k: Qint[4]) -> Qint[4]:
    return k >> 3
"""
        qf = qlassf(f, compiler=self.compiler)
        algo = Simon(qf)

        qc = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc, shots=1024)
        counts_readable = algo.decode_counts(counts)

        for x in [0, 8]:
            self.assertEqual(x in counts_readable, True)
            self.assertEqual(counts_readable[x] > 400, True)
        self.assertEqual(algo.output_qubits, [0, 1, 2, 3])
