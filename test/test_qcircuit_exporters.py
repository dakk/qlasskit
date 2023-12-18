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


class TestQCircuitExportQASM(unittest.TestCase):
    def test_export_qasm(self):
        qc = QCircuit()
        a, b = qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.cx(a, b)
        qasm_c = qc.export("gate", "qasm")
        self.assertEqual(qasm_c, "gate qc q0 q1 {\n\tx q0\n\tcx q0 q1\n}\n\n")

    def test_export_qasm_toffoli(self):
        qc = QCircuit()
        a, b, c = qc.add_qubit("a"), qc.add_qubit("b"), qc.add_qubit("c")
        qc.x(a)
        qc.x(b)
        qc.ccx(a, b, c)
        qasm_c = qc.export("gate", "qasm")
        self.assertEqual(qasm_c, "gate qc a b c {\n\tx a\n\tx b\n\tccx a b c\n}\n\n")


class TestQCircuitExportSympy(unittest.TestCase):
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


class TestQCircuitExportQiskit(unittest.TestCase):
    def test_export_qiskit(self):
        qc = QCircuit()
        a, b = qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.cx(a, b)
        circ = qc.export("circuit", "qiskit")
        counts = qiskit_measure_and_count(circ, shots=1)
        self.assertDictEqual(counts, {"11": 1})

    def test_export_qiskit_toffoli(self):
        qc = QCircuit()
        a, b, c = qc.add_qubit(), qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.x(b)
        qc.ccx(a, b, c)
        circ = qc.export("circuit", "qiskit")
        counts = qiskit_measure_and_count(circ, shots=1)
        self.assertDictEqual(counts, {"111": 1})


class TestQCircuitExportCirq(unittest.TestCase):
    def test_export_cirq_circuit(self):
        qc = QCircuit()
        a, b = qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.cx(a, b)
        circ = qc.export("circuit", "cirq")

        import cirq
        import numpy as np

        circ.append(cirq.measure_each(circ.all_qubits()))
        simulator = cirq.Simulator()
        result = simulator.run(circ)

        self.assertDictEqual(
            result.records,
            {
                "q(0)": np.array([[[1]]], dtype=np.int8),
                "q(1)": np.array([[[1]]], dtype=np.int8),
            },
        )

    def test_export_cirq_gate(self):
        qc = QCircuit()
        a, b = qc.add_qubit(), qc.add_qubit()
        qc.x(a)
        qc.cx(a, b)
        gat = qc.export("gate", "cirq")

        import cirq
        import numpy as np

        qreg = cirq.LineQubit.range(2)
        circ = cirq.Circuit(gat().on(*qreg))

        circ.append(cirq.measure_each(circ.all_qubits()))
        simulator = cirq.Simulator()
        result = simulator.run(circ)
        self.assertDictEqual(
            result.records,
            {
                "q(0)": np.array([[[1]]], dtype=np.int8),
                "q(1)": np.array([[[1]]], dtype=np.int8),
            },
        )


class TestQCircuitExportPennylane(unittest.TestCase):
    def test_export_pennylane_circuit(self):
        import pennylane as qml

        qc = QCircuit()
        a, b = qc.add_qubit(), qc.add_qubit()
        qc.h(a)
        qc.cx(a, b)
        tape = qc.export("circuit", "pennylane")
        tape = qml.tape.QuantumTape(tape.operations, [qml.probs()])

        dev = qml.device("default.qubit", wires=2)
        r = qml.execute([tape], dev, gradient_fn=None)

        self.assertAlmostEqual(r[0][0], 0.5)
        self.assertAlmostEqual(r[0][3], 0.5)
