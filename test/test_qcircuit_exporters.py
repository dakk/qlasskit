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

import cirq
import numpy as np
import pennylane as qml
from parameterized import parameterized_class
from qutip import basis, tensor
from sympy.physics.quantum.qapply import qapply
from sympy.physics.quantum.qubit import Qubit, measure_all

from qlasskit.qcircuit import QCircuit

from .utils import qiskit_measure_and_count


def cx_circuit():
    qc = QCircuit()
    a, b = qc.add_qubit(), qc.add_qubit()
    qc.x(a)
    qc.cx(a, b)
    return qc


def ccx_circuit():
    qc = QCircuit()
    a, b, c = qc.add_qubit("a"), qc.add_qubit("b"), qc.add_qubit("c")
    qc.x(a)
    qc.x(b)
    qc.ccx(a, b, c)
    return qc


def bell_circuit():
    qc = QCircuit()
    a, b = qc.add_qubit("a"), qc.add_qubit("b")
    qc.h(a)
    qc.cx(a, b)
    return qc


def qft_circuit():
    qc = QCircuit()
    a, b, c = qc.add_qubit("a"), qc.add_qubit("b"), qc.add_qubit("c")
    qc.qft([a, b, c])
    qc.iqft([a, b, c])
    return qc


@parameterized_class(
    ("qc", "result"),
    [
        (cx_circuit(), "gate qc q0 q1 {\n\tx q0\n\tcx q0 q1\n}\n\n"),
        (ccx_circuit(), "gate qc a b c {\n\tx a\n\tx b\n\tccx a b c\n}\n\n"),
        (bell_circuit(), "gate qc a b {\n\th a\n\tcx a b\n}\n\n"),
        (
            qft_circuit(),
            (
                "gate qc a b c {\n\th a\n\tcp(1.57) b a\n\tcp(0.79) c a\n\th b\n"
                "\tcp(1.57) c b\n\th c\n\tswap a c\n\tswap a c\n\th c\n"
                "\tcp(-1.57) c b\n\th b\n\tcp(-0.79) c a\n\tcp(-1.57) b a\n\th a\n}\n\n"
            ),
        ),
    ],
)
class TestQCircuitExportQASM(unittest.TestCase):
    def test_export_qasm_gate(self):
        qasm_c = self.qc.export("gate", "qasm")
        self.assertEqual(qasm_c, self.result)

    def test_export_qasm_circuit(self):
        qasm_c = self.qc.export("circuit", "qasm")

        call = "qc "
        call += ",".join([f"q[{x}]" for x in range(self.qc.num_qubits)])
        self.assertEqual(qasm_c, f"OPENQASM 3.0;\n\n{self.result}{call};\n")


@parameterized_class(
    ("qc", "result"),
    [
        (cx_circuit(), [(Qubit("11"), 1)]),
        (ccx_circuit(), [(Qubit("111"), 1)]),
        (bell_circuit(), [(Qubit("00"), 1 / 2), (Qubit("11"), 1 / 2)]),
        # (qft_circuit(), [(Qubit("000"), 1)]),
    ],
)
class TestQCircuitExportSympy(unittest.TestCase):
    def test_export_sympy_circuit(self):
        sym_circ = self.qc.export("circuit", "sympy")
        statev = qapply(sym_circ)
        meas = measure_all(statev)
        self.assertEqual(meas, self.result)

    def test_export_sympy_gate(self):
        sym_circ = self.qc.export("gate", "sympy")
        statev = qapply(sym_circ * Qubit("0" * self.qc.num_qubits))
        meas = measure_all(statev)
        self.assertEqual(meas, self.result)


@parameterized_class(
    ("qc", "result"),
    [
        (cx_circuit(), {"11": 1}),
        (ccx_circuit(), {"111": 1}),
        (qft_circuit(), {"000": 1}),
    ],
)
class TestQCircuitExportQiskit(unittest.TestCase):
    def test_export_qiskit(self):
        circ = self.qc.export("circuit", "qiskit")
        counts = qiskit_measure_and_count(circ, shots=1)
        self.assertDictEqual(counts, self.result)


@parameterized_class(
    ("qc", "result"),
    [
        (
            cx_circuit(),
            {
                "q(0)": np.array([[[1]]], dtype=np.int8),
                "q(1)": np.array([[[1]]], dtype=np.int8),
            },
        ),
        (
            ccx_circuit(),
            {
                "q(0)": np.array([[[1]]], dtype=np.int8),
                "q(1)": np.array([[[1]]], dtype=np.int8),
                "q(2)": np.array([[[1]]], dtype=np.int8),
            },
        ),
        (
            qft_circuit(),
            {
                "q(0)": np.array([[[0]]], dtype=np.int8),
                "q(1)": np.array([[[0]]], dtype=np.int8),
                "q(2)": np.array([[[0]]], dtype=np.int8),
            },
        ),
    ],
)
class TestQCircuitExportCirq(unittest.TestCase):
    def test_export_cirq_circuit(self):
        circ = self.qc.export("circuit", "cirq")

        circ.append(cirq.measure_each(circ.all_qubits()))
        simulator = cirq.Simulator()
        result = simulator.run(circ)

        self.assertDictEqual(
            result.records,
            self.result,
        )

    def test_export_cirq_gate(self):
        gat = self.qc.export("gate", "cirq")

        qreg = cirq.LineQubit.range(self.qc.num_qubits)
        circ = cirq.Circuit(gat().on(*qreg))

        circ.append(cirq.measure_each(circ.all_qubits()))
        simulator = cirq.Simulator()
        result = simulator.run(circ)
        self.assertDictEqual(
            result.records,
            self.result,
        )


@parameterized_class(
    ("qc", "result", "wires"),
    [
        (cx_circuit(), [0, 0, 0, 1], 2),
        (ccx_circuit(), [0, 0, 0, 0, 0, 0, 0, 1], 3),
        (bell_circuit(), [0.5, 0, 0, 0.5], 2),
        (qft_circuit(), [1, 0, 0, 0, 0, 0, 0, 0], 3),
    ],
)
class TestQCircuitExportPennylane(unittest.TestCase):
    def test_export_pennylane_circuit(self):
        tape = self.qc.export("circuit", "pennylane")
        tape = qml.tape.QuantumTape(tape.operations, [qml.probs()])

        dev = qml.device("default.qubit", wires=self.wires)
        r = qml.execute([tape], dev, gradient_fn=None)

        self.assertEqual(len(r[0]), len(self.result))

        for a, b in zip(r[0], self.result):
            self.assertAlmostEqual(a, b)


@parameterized_class(
    ("qc", "result"),
    [
        (cx_circuit(), [0, 0, 0, 1]),
        (ccx_circuit(), [0, 0, 0, 0, 0, 0, 0, 1]),
        (bell_circuit(), [0.70710678, 0, 0, 0.70710678]),
        (qft_circuit(), [1, 0, 0, 0, 0, 0, 0, 0]),
    ],
)
class TestQCircuitExportQutip(unittest.TestCase):
    def test_export_qutip_circuit(self):
        qc = self.qc.export("circuit", "qutip")
        zero_state = tensor(*[basis(2, 0) for i in range(self.qc.num_qubits)])

        result = qc.run_statistics(state=zero_state)
        states = result.get_final_states()
        probabilities = result.get_probabilities()

        self.assertEqual(probabilities, [1])

        for i in zip(states[0].data.to_array(), self.result):
            self.assertAlmostEqual(float(i[0][0]), i[1])
