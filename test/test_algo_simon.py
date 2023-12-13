# Copyright 2023 Davide Gessa

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

from parameterized import parameterized_class

from qlasskit import Qint2, Qint4, qlassf
from qlasskit.algorithms import Simon
from qlasskit.compiler import SupportedCompilers

from .utils import ENABLED_COMPILERS, qiskit_measure_and_count


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestAlgoSimon(unittest.TestCase):
    def test_simon(self):
        f = """
def hash(k: Qint4) -> Qint4:
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
