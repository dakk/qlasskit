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

import ast
import unittest

from sympy import Symbol
from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.qubit import Qubit, measure_all

from qlasskit.qcircuit import QCircuit, QCircuitEnhanced, gates

from .utils import qiskit_measure_and_count


class TestQCircuit(unittest.TestCase):
    def test_base(self):
        qc = QCircuit()
        qc.ccx(qc.add_qubit(), qc.add_qubit(), qc.add_qubit())
        self.assertEqual(qc.num_qubits, 3)

    def test_base_mapping(self):
        qc = QCircuit()
        a, b, c = qc.add_qubit("a"), qc.add_qubit("b"), qc.add_qubit(Symbol("c"))
        qc.ccx("a", Symbol("b"), c)
        self.assertEqual(qc.num_qubits, 3)
        self.assertTrue(isinstance(qc.gates[0][0], gates.CCX))
        self.assertEqual(qc.gates[0][1:], ([0, 1, 2], None))

    def test_duplicate_qubit(self):
        qc = QCircuit()
        a, b = qc.add_qubit("a"), qc.add_qubit("b")
        self.assertRaises(Exception, lambda qc: qc.toffoli(a, b, a), qc)

    def test_mapping(self):
        qc = QCircuit(4)
        qc.ccx("q0", "q1", "q2")

    def test_augassign(self):
        qc = QCircuit(1)
        qc += gates.apply(gates.X(), [0])

    def test_augassign_othercirc(self):
        qc = QCircuit(1)
        qc += gates.apply(gates.X(), [0])

        qc2 = QCircuit(1)
        qc2 += qc

    def test_get_key_by_index(self):
        qc = QCircuit()
        a, b = qc.add_qubit("a"), qc.add_qubit("b")
        self.assertRaises(Exception, lambda qc: qc.get_key_by_index(3), qc)
        self.assertEqual(qc.get_key_by_index(0), "a")

    def test_add_free_ancilla(self):
        qc = QCircuitEnhanced()
        a = qc.add_ancilla(is_free=True)
        b = qc.get_free_ancilla()
        self.assertEqual(a, b)


class TestQCircuitUncomputing(unittest.TestCase):
    def test1(self):
        qc = QCircuitEnhanced()
        a, b, c, d = (
            qc.add_qubit(),
            qc.add_qubit(),
            qc.add_ancilla(is_free=False),
            qc.add_ancilla(is_free=False),
        )
        f = qc.add_qubit("res")
        qc.mcx([a, b], c)
        qc.mcx([a, b, c], d)
        qc.cx(d, f)
        qc.uncompute([c, d])
        # qc.draw()

    def test2(self):
        qc = QCircuitEnhanced()
        q = [qc.add_qubit() for x in range(4)]
        a = [qc.add_ancilla(is_free=False) for x in range(4)]
        r = qc.add_qubit()

        qc.mcx(q, a[0])
        qc.mcx(q + [a[0]], a[1])
        qc.mcx(q + a[:2], a[2])
        qc.mcx(q + a[:3], a[3])
        qc.cx(a[3], r)
        qc.uncompute(a)

        self.assertEqual(len(qc.free_ancilla_lst), len(a))
        # qc.draw()

    def test_uncompute_all(self):
        qc = QCircuitEnhanced()
        q = [qc.add_qubit() for x in range(4)]
        a = [qc.add_ancilla(is_free=False) for x in range(4)]
        r = qc.add_qubit()

        qc.mcx(q, a[0])
        qc.mcx(q + [a[0]], a[1])
        qc.mcx(q + a[:2], a[2])
        qc.mcx(q + a[:3], a[3])
        qc.cx(a[3], r)
        qc.uncompute(a)
        qc.uncompute_all([r])
        # qc.draw()
