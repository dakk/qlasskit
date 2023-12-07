# Copyright 2023 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

import copy

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any, List, Literal, Tuple, Union

from sympy import Symbol

from . import SupportedFramework, gates
from .gates import QGate


class QCircuit:
    def __init__(self, num_qubits=0, name="qc", native=None):
        """Initialize a quantum circuit.

        Args:
            num_qubits (int, optional): The number of qubits in the circuit. Defaults to 0.

        """
        self.name: str = name
        self.num_qubits: int = num_qubits
        self.gates: List[gates.AppliedGate] = []
        self.gates_computed: List[gates.AppliedGate] = []
        self.qubit_map = {}

        for x in range(num_qubits):
            self.qubit_map[f"q{x}"] = x

        self.__native = native

    @property
    def num_gates(self):
        return len(self.gates)

    def get_key_by_index(self, i: int):
        """Return the qubit name given its index"""
        for key in self.qubit_map:
            if self.qubit_map[key] == i:
                return key
        raise Exception(f"Qubit with index {i} not found")

    def __repr__(self):
        """Return a string representation of the QCircuit"""
        return (
            f"QCircuit<{self.name}>({self.num_gates} gates, {self.num_qubits} qubits)"
        )

    def __contains__(self, key: Union[str, Symbol, int]):
        """Return True if the circuit contain a qubit with a given name/symbol"""
        if isinstance(key, str):
            return key in self.qubit_map
        elif isinstance(key, Symbol):
            return key.name in self.qubit_map
        return False

    def __delitem__(self, key: Union[str, Symbol, int]):
        """Remove a mapping key=>qubit"""
        if isinstance(key, str):
            del self.qubit_map[key]
        elif isinstance(key, Symbol):
            del self.qubit_map[key.name]

    def __setitem__(self, key: Union[str, Symbol, int], qubit: int):
        """Set a mapping key=>qubit"""
        if isinstance(key, str):
            self.qubit_map[key] = qubit
        elif isinstance(key, Symbol):
            self.qubit_map[key.name] = qubit

    def __getitem__(self, key: Union[str, Symbol, int]):
        """Return the qubit index given its name or index"""
        if isinstance(key, str):
            return self.qubit_map[key]
        elif isinstance(key, Symbol):
            return self.qubit_map[key.name]
        else:
            return key

    def __add__(self, qc: "QCircuit") -> "QCircuit":
        """Create a new QCircuit that merges two"""
        nqc = copy.deepcopy(self)
        nqc += qc
        return nqc

    def copy(self) -> "QCircuit":
        self.__native = None
        return copy.deepcopy(self)

    def __iadd__(self, other: Union[gates.AppliedGate, "QCircuit"]):  # type: ignore
        """AugAssign between a qcircuit and a AppliedGate|QCircuit"""
        if isinstance(other, Tuple):  # type: ignore
            self.append(other[0], other[1], other[2])
        elif isinstance(other, QCircuit):  # type: ignore
            if other.num_qubits > self.num_qubits:
                raise Exception(
                    f"Other circuit has too many qubits {other.num_qubits} > {self.num_qubits}"
                )

            self.gates.extend(other.gates)
            self.gates_computed.extend(other.gates_computed)

            for s, q in other.qubit_map.items():
                if s not in self.qubit_map:
                    self.qubit_map[s] = q

        return self

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

    def append(self, gate: QGate, qubits: List[int], param: Any = None):
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

        qs = set()
        for q in qubits:
            if q in qs:
                raise Exception(f"duplicate qubit in gate append: {qubits}")
            qs.add(q)

        applied = gates.apply(gate, qubits, param)
        self.gates.append(applied)

        if not isinstance(gate, gates.NopGate):
            self.gates_computed.append(applied)

    def barrier(self, label=None):
        """Add a barrier to the circuit"""
        self.append(gates.Barrier(), [], label)

    def h(self, w: int):
        """H gate"""
        w = self[w]
        self.append(gates.H(), [w])

    def z(self, w: int):
        """Z gate"""
        w = self[w]
        self.append(gates.Z(), [w])

    def x(self, w: int):
        """X gate"""
        w = self[w]
        self.append(gates.X(), [w])

    def y(self, w: int):
        """Y gate"""
        w = self[w]
        self.append(gates.Y(), [w])

    def t(self, w: int):
        """T gate"""
        w = self[w]
        self.append(gates.T(), [w])

    def s(self, w: int):
        """S gate"""
        w = self[w]
        self.append(gates.S(), [w])

    def cx(self, w1, w2):
        """CX gate"""
        w1, w2 = self[w1], self[w2]
        self.append(gates.CX(), [w1, w2])

    def ccx(self, w1, w2, w3):
        """CCX gate"""
        w1, w2, w3 = self[w1], self[w2], self[w3]
        self.append(gates.CCX(), [w1, w2, w3])

    def mctrl(self, g, wl: List[int], target, param=None):
        """Multi controlled gate"""
        target = self[target]
        wl = list(map(lambda w: self[w], wl))
        self.append(gates.MCtrl(g, len(wl)), wl + [target], param)

    def mcx(self, wl: List[int], target):
        """Multi CX gate"""
        target = self[target]
        wl = list(map(lambda w: self[w], wl))
        self.append(gates.MCX(len(wl)), wl + [target])

    def export(
        self,
        mode: Literal["circuit", "gate"] = "circuit",
        framework: SupportedFramework = "qiskit",
    ):
        """Exports the circuit to another framework.

        Args:
            mode (Literal["circuit", "gate"], optional): The export mode, which can be "circuit"
                or "gate". Defaults to "circuit".
            framework (SupportedFramework, optional): The target framework for export,
                either "qiskit", "sympy", "cirq", "qasm". Defaults to "qiskit".

        Returns:
            Any: The exported circuit or gate representation in the specified framework.

        Raises:
            Exception: If the specified framework is not supported.

        """

        if framework == "qiskit":
            from .exporter_qiskit import QiskitExporter

            return QiskitExporter().export(self, mode)
        elif framework == "sympy":
            from .exporter_sympy import SympyExporter

            return SympyExporter().export(self, mode)
        elif framework == "qasm":
            from .exporter_qasm import QasmExporter

            return QasmExporter().export(self, mode)
        elif framework == "cirq":
            from .exporter_cirq import CirqExporter

            return CirqExporter().export(self, mode)
        else:
            raise Exception(f"Framework {framework} not supported")

    def draw(self):
        """Draw the circuit"""
        if self.__native:
            print(self.__native)
        else:
            qc = self.export("circuit", "qiskit")
            print(qc.draw("text"))
