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

from qlasskit import QCircuit
from qlasskit.decompiler import circuit_boolean_optimizer
from qlasskit.qcircuit import gates

from .utils import qiskit_unitary


class TestCircuitBooleanOptimizer(unittest.TestCase):
    def test_circuit_boolean_optimizer(self):
        qc = QCircuit(3)
        qc.h(2)
        qc.barrier()
        qc.x(0)
        qc.cx(0, 1)
        qc.x(0)
        qc.cx(0, 1)
        qc.barrier()
        qc.h(2)
        qc.h(1)
        qc.h(0)
        qc.barrier()
        qc.x(1)
        qc.cx(1, 2)
        qc.x(1)
        qc.cx(1, 2)

        qc_n = circuit_boolean_optimizer(qc)

        qc_un = qiskit_unitary(qc.export())
        qc_n_un = qiskit_unitary(qc_n.export())

        self.assertEqual(qc_n.num_gates, 6)
        self.assertEqual(qc_un, qc_n_un)

    def test_circuit_boolean_optimizer2(self):
        qc = QCircuit(3)
        qc.ccx(0, 1, 2)
        qc.x(0)
        qc.x(1)
        qc.ccx(0, 1, 2)
        qc_n = circuit_boolean_optimizer(qc)

        qc_un = qiskit_unitary(qc.export())
        qc_n_un = qiskit_unitary(qc_n.export())

        self.assertEqual(qc_n.num_gates, 4)
        self.assertEqual(qc_un, qc_n_un)

    def test_circuit_boolean_optimizer_random_x(self):
        for i in range(16):
            qc = QCircuit.random(3, 8, [gates.X])
            qc_n = circuit_boolean_optimizer(qc)
            self.assertLessEqual(qc_n.num_gates, 3)

    # def test_circuit_boolean_optimizer_random_x_cx(self):
    #     qc = QCircuit.random(3, 8, [gates.X, gates.CX])
    #     qc.draw()

    #     qc_n = circuit_boolean_optimizer(qc)
    #     qc_n.draw()
