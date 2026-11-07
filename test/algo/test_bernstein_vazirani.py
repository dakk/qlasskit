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

from parameterized import parameterized, parameterized_class

from qlasskit import QlassF
from qlasskit.algorithms import BernsteinVazirani, secret_oracle

from ..utils import ENABLED_COMPILERS, qiskit_measure_and_count


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestAlgoBernsteinVazirani(unittest.TestCase):
    def test_secret_oracle(self):
        isize = 4
        secret = 12

        f = f"def oracle(x: Qint[{isize}]) -> bool:\n"
        f += f"  s=Qint{isize}({secret})\n"
        f += "  return ("
        f += "^".join(f"(x[{i}]&s[{i}])" for i in range(isize))
        f += ")"

        qf = QlassF.from_function(f)
        qf2 = secret_oracle(isize, secret)
        self.assertEqual(qf.export("qasm"), qf2.export("qasm"))

    @parameterized.expand(
        [
            (4, 14),
            (4, 12),
            (4, 15),
            (8, 122),
        ]
    )
    def test_bernstein_vazirani_secret(self, isize, secret):
        algo = BernsteinVazirani(secret_oracle(isize, secret))

        qc_algo = algo.circuit().export("circuit", "qiskit")
        counts = qiskit_measure_and_count(qc_algo, shots=1024)
        counts_readable = algo.decode_counts(counts)

        self.assertTrue(secret in counts_readable)
        self.assertEqual(counts_readable[secret], 1024)
