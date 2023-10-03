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
from typing import List, Literal, Union

from sympy import Symbol
from sympy.physics.quantum.gate import CNOT, H, T, X
from sympy.physics.quantum.qubit import Qubit


class QCircuit:
    def __init__(self, num_qubits=0):
        """Initialize a quantum circuit.

        Args:
            num_qubits (int, optional): The number of qubits in the circuit. Defaults to 0.

        """
        self.num_qubits = num_qubits
        self.gates = []
        self.qubit_map = {}

        self.ancillas = set()
        self.free_ancillas = set()

        for x in range(num_qubits):
            self.qubit_map[f"q{x}"] = x

    def __add__(self, other: "QCircuit"):
        """Combine two quantum circuits.

        Args:
            other (QCircuit): The other quantum circuit to be combined with this one.

        """
        self.num_qubits = max(self.num_qubits, other.num_qubits)
        self.gates.extend(other.gates)

    def __getitem__(self, key: Union[str, Symbol, int]):
        """Return the qubit index given its name or index"""
        if isinstance(key, str):
            return self.qubit_map[key]
        elif isinstance(key, Symbol):
            return self.qubit_map[key.name]
        else:
            return key

    def add_ancilla(self, name=None):
        """Add an ancilla qubit"""
        i = self.add_qubit(name if name else f"anc_{len(self.ancillas)}")
        self.ancillas.add(i)
        self.free_ancillas.add(i)
        return i

    def free_ancilla(self, w):
        """Freeing of an ancilla qubit"""
        w = self[w]
        if w not in self.ancillas:
            raise Exception(f"Qubit {w} is not in the ancilla set")

        if w in self.free_ancilla:
            raise Exception(f"Ancilla {w} is already free")

        self.uncompute(w)
        self.free_ancillas.add(w)

    def get_free_ancilla(self):
        """Get the first free ancilla available"""
        if len(self.free_ancillas) == 0:
            return self.add_ancilla()
        return self.free_ancillas.pop()

    def uncompute(self, w):
        """Uncompute a specific qubit.

        Args:
            w (int): The index of the qubit to be uncomputed.
        """
        w = self[w]
        raise Exception("Not yet implemented")

    def add_qubit(self, name=None):
        """Add a qubit to the circuit.

        Args:
            name (Union[Symbol,str], optional): the qubit symbol/name

        Returns:
            int: The index of the added qubit.

        """
        if isinstance(name, Symbol):
            name = name.name

        name = name if name is not None else f"q{self.num_qubits}"
        self.qubit_map[name] = self.num_qubits

        self.num_qubits += 1
        return self.num_qubits - 1

    def append(self, gate_name: str, qubits: List[int]):
        """Append a gate operation to the circuit.

        Args:
            gate_name (str): The name of the gate to be applied.
            qubits (List[int]): The list of qubit indices where the gate is applied.

        Raises:
            Exception: If a qubit index is out of range.

        """
        for x in qubits:
            if self.num_qubits is None or x > self.num_qubits:
                raise Exception(f"qubit {x} not present")

        self.gates.append((gate_name, qubits))

    def barrier(self):
        """Add a barrier to the circuit"""
        self.append("bar")

    def x(self, w: int):
        """X gate"""
        w = self[w]
        self.append("x", [w])

    def cx(self, w1, w2):
        """CX gate"""
        w1, w2 = self[w1], self[w2]
        self.append("cx", [w1, w2])

    def ccx(self, w1, w2, w3):
        """CCX gate"""
        w1, w2, w3 = self[w1], self[w2], self[w3]
        self.append("ccx", [w1, w2, w3])

    def fredkin(self, w1, w2, w3):
        """Fredkin (cswap) gate"""
        w1, w2, w3 = self[w1], self[w2], self[w3]
        self.append("fredkin", [w1, w2, w3])

    def __sympy_export(self):
        """Internal function for exporting sympy quantum expressions"""

        def toffoli(q0, q1, q2):
            # TODO: investigate why t**-1 raises max recursion on qapply
            return (
                H(q2)
                * CNOT(q2, q1)
                * T(q2) ** -1
                * CNOT(q0, q2)
                * T(q2)
                * CNOT(q1, q2)
                * T(q2) ** -1
                * CNOT(q0, q2)
                * T(q1)
                * T(q2)
                * H(q2)
                * CNOT(q0, q1)
                * T(q0)
                * T(q1) ** -1
                * CNOT(q0, q1)
            )

        qstate = Qubit("0" * self.num_qubits)

        for g, w in self.gates:
            ga = None
            if g == "x":
                ga = X(w[0])
            elif g == "cx":
                ga = CNOT(w[0], w[1])
            elif g == "ccx":
                raise Exception("Not implemented yet")
            elif g == "fredkin":
                raise Exception("Not implemented yet")
            if ga:
                qstate = ga * qstate

        return qstate

    def __qiskit_export(self, mode: Literal["circuit", "gate"]):
        """Internal function for exporting qiskit quantum circuit"""
        from qiskit import QuantumCircuit

        qc = QuantumCircuit(self.num_qubits, 0)

        for g, w in self.gates:
            if g == "x":
                qc.x(w[0])
            elif g == "cx":
                qc.cx(w[0], w[1])
            elif g == "ccx":
                qc.ccx(w[0], w[1], w[2])
            elif g == "bar":
                qc.barrier()
            elif g == "fredkin":
                qc.fredkin(w[0], w[1], w[2])

        if mode == "gate":
            return qc.to_gate()
        elif mode == "circuit":
            return qc
        else:
            raise Exception(f"Uknown export mode: {mode}")

    def export(self, mode: Literal["circuit", "gate"] = "circuit", framework="qiskit"):
        """Exports the circuit to another framework.

        Args:
            mode (Literal["circuit", "gate"], optional): The export mode, which can be "circuit"
                or "gate". Defaults to "circuit".
            framework (str, optional): The target framework for export, either "qiskit" or "sympy".
                Defaults to "qiskit".

        Returns:
            Any: The exported circuit or gate representation in the specified framework.

        Raises:
            Exception: If the specified framework is not supported.

        """

        if framework == "qiskit":
            return self.__qiskit_export(mode)
        elif framework == "sympy":
            return self.__sympy_export()
        else:
            raise Exception(f"Framework {framework} not supported")
