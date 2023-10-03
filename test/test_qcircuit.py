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

from qlasskit import QCircuit

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
        self.assertEqual(qc.gates, [("ccx", [0, 1, 2])])


class TestQCircuitExport(unittest.TestCase):
    def test_export_sympy(self):
        qc = QCircuit()
        a, b = qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.cx(a, b)
        sym_circ = qc.export("circuit", "sympy")
        statev = qapply(sym_circ)
        meas = measure_all(statev)
        self.assertEqual(meas, [(Qubit("11"), 1)])

    # def test_export_sympy_toffoli(self):
    #     qc = QCircuit()
    #     a, b, c = qc.add_qubit(), qc.add_qubit(), qc.add_qubit()
    #     qc.x(a)
    #     qc.x(b)
    #     qc.ccx(a, b, c)
    #     sym_circ = qc.export("circuit", "sympy")
    #     statev = qapply(sym_circ)
    #     meas = measure_all(statev)
    #     self.assertEqual(meas, [(Qubit("111"), 1)])

    def test_export_qiskit(self):
        qc = QCircuit()
        a, b = qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.cx(a, b)
        circ = qc.export("circuit", "qiskit")
        counts = qiskit_measure_and_count(circ)
        self.assertDictEqual(counts, {"11": 1024})

    def test_export_qiskit_toffoli(self):
        qc = QCircuit()
        a, b, c = qc.add_qubit(), qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.x(b)
        qc.ccx(a, b, c)
        circ = qc.export("circuit", "qiskit")
        counts = qiskit_measure_and_count(circ)
        self.assertDictEqual(counts, {"111": 1024})

    def test_export_qiskit_fredkin(self):
        qc = QCircuit()
        a, b, c = qc.add_qubit(), qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.x(b)
        qc.fredkin(a, b, c)
        circ = qc.export("circuit", "qiskit")
        counts = qiskit_measure_and_count(circ)
        self.assertDictEqual(counts, {"101": 1024})
