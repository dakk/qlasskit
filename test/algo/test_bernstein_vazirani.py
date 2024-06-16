# Copyright 2023-2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
