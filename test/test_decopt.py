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

import itertools
import random
import unittest

from qlasskit import QCircuit, boolopt, qlassf
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

            qc_un = qiskit_unitary(qc.export())
            qc_n_un = qiskit_unitary(qc_n.export())
            self.assertEqual(qc_un, qc_n_un)

    def test_circuit_boolean_optimizer_random_2(self):
        qc = QCircuit(3)
        qc.x(2)
        qc.cx(1, 0)
        qc.x(0)
        qc.cx(1, 0)
        qc.x(0)
        qc.x(1)
        qc.x(0)
        qc.cx(2, 1)
        # qc.ccx(0,1,2)
        # qc.draw()

        qc_n = circuit_boolean_optimizer(qc)
        # print(qc_n, qc_n.gates)
        # qc_n.draw()

        qc_un = qiskit_unitary(qc.export())
        qc_n_un = qiskit_unitary(qc_n.export())
        self.assertEqual(qc_un, qc_n_un)

    def test_circuit_boolean_optimizer_random_x_cx(self):
        g_simp = 0

        possib = [
            (gates.CX, x[0], x[1]) for x in itertools.permutations([0, 1, 2], r=2)
        ]
        possib += [(gates.X, x[0]) for x in itertools.permutations([0, 1, 2], r=1)]

        for i in random.choices(
            list(itertools.combinations_with_replacement(possib, r=8)), k=32
        ):
            qc = QCircuit(3)
            for g in i:
                qc.append(g[0](), g[1:])

            qc_n = circuit_boolean_optimizer(qc)
            g_simp += qc.num_gates - qc_n.num_gates

            qc_un = qiskit_unitary(qc.export())

            qc_n_un = qiskit_unitary(qc_n.export())
            self.assertEqual(qc_un, qc_n_un)

        # print(g_simp)

    def test_circuit_boolean_optimizer_duplicate_qubit_bug(self):
        s = "def qf(a: Qint[4]) -> Qint[4]:\n\treturn a * a"
        qf = qlassf(s)
        qc = qf.circuit()
        nc = circuit_boolean_optimizer(qc)
        self.assertEqual(qc.num_gates, nc.num_gates)
        self.assertEqual(qc.num_qubits, nc.num_qubits)

        s = "def qf(a: Qint[4]) -> Qint[4]:\n\treturn a + 2 + 1 + 3"
        qf = qlassf(s)
        qc = qf.circuit()
        nc = circuit_boolean_optimizer(qc)
        self.assertEqual(qc.num_gates, nc.num_gates)
        self.assertEqual(qc.num_qubits, nc.num_qubits)

    def test_decopt_preserve_output_qubit(self):
        f = (
            "def test(a: Qlist[bool, 2]) -> bool:\n\ts = True\n\tfor i in a:\n"
            "\t\ts = s and i\n\treturn s"
        )

        qf = qlassf(f, to_compile=True, bool_optimizer=boolopt.fastOptimizer)
        qc = circuit_boolean_optimizer(qf.circuit(), preserve=[0, 1])

        self.assertEqual(len(qc.gates), 1)

        # TODO: fix this, we need to detect output during compilation
        # self.assertEqual(qc.gates[0][1], [0, 1, 6])
