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
    def __init__(self, num_qubits=0, name="qc"):
        """Initialize a quantum circuit.

        Args:
            num_qubits (int, optional): The number of qubits in the circuit. Defaults to 0.

        """
        self.name = name
        self.num_qubits = num_qubits
        self.gates = []
        self.gates_computed = []
        self.qubit_map = {}

        self.ancilla_lst = set()
        self.free_ancilla_lst = set()
        self.marked_ancillas = set()

        for x in range(num_qubits):
            self.qubit_map[f"q{x}"] = x

    def get_key_by_index(self, i: int):
        """Return the qubit name given its index"""
        for key in self.qubit_map:
            if self.qubit_map[key] == i:
                return key
        raise Exception(f"Qubit with index {i} not found")

    def __contains__(self, key: Union[str, Symbol, int]):
        if isinstance(key, str):
            return key in self.qubit_map
        elif isinstance(key, Symbol):
            return key.name in self.qubit_map
        return False

    def __delitem__(self, key: Union[str, Symbol, int]):
        if isinstance(key, str):
            del self.qubit_map[key]
        elif isinstance(key, Symbol):
            del self.qubit_map[key.name]

    def __setitem__(self, key: Union[str, Symbol, int], val):
        if isinstance(key, str):
            self.qubit_map[key] = val
        elif isinstance(key, Symbol):
            self.qubit_map[key.name] = val

    def __getitem__(self, key: Union[str, Symbol, int]):
        """Return the qubit index given its name or index"""
        if isinstance(key, str):
            return self.qubit_map[key]
        elif isinstance(key, Symbol):
            return self.qubit_map[key.name]
        else:
            return key

    def remove_identities(self):
        result = []
        i = 0
        len_g = len(self.gates)
        while i < len_g:
            if i < (len_g - 1) and self.gates[i] == self.gates[i + 1]:
                if result[-1][0] == "bar":
                    result.pop()
                i += 2
            elif (
                i < (len_g - 2)
                and self.gates[i] == self.gates[i + 2]
                and self.gates[i + 1][0] == "bar"
            ):
                if result[-1][0] == "bar":
                    result.pop()
                i += 3
            else:
                result.append(self.gates[i])
                i += 1

        self.gates = result

    def add_ancilla(self, name=None, is_free=True):
        """Add an ancilla qubit"""
        i = self.add_qubit(name if name else f"anc_{len(self.ancilla_lst)}")
        self.ancilla_lst.add(i)
        if is_free:
            self.free_ancilla_lst.add(i)
        return i

    def get_free_ancilla(self):
        """Get the first free ancilla available"""
        if len(self.free_ancilla_lst) == 0:
            anc = self.add_ancilla(is_free=False)
        else:
            anc = self.free_ancilla_lst.pop()

        return anc

    def mark_ancilla(self, w):
        if w in self.ancilla_lst:
            self.marked_ancillas.add(w)

    def uncompute(self, to_mark=[]):
        """Uncompute all the marked ancillas plus the to_mark list"""
        [self.mark_ancilla(x) for x in to_mark]

        self.barrier(label="un")

        uncomputed = set()
        new_gates_comp = []
        not_to_uncompute = set()

        for g, ws in self.gates_computed[::-1]:
            if ws[-1] in self.marked_ancillas and not all(
                [ww in self.marked_ancillas for ww in ws[:-1]]
            ):
                not_to_uncompute.add(ws[-1])

        for g, ws in self.gates_computed[::-1]:
            if ws[-1] in self.marked_ancillas and ws[-1] not in not_to_uncompute:
                uncomputed.add(ws[-1])
                self.append(g, ws)
            else:
                new_gates_comp.append((g, ws))

        for x in uncomputed:
            self.free_ancilla_lst.add(x)
        self.marked_ancillas = self.marked_ancillas - uncomputed
        self.gates_computed = new_gates_comp[::-1]

        if len(uncomputed) == 0:
            self.gates.pop()

        return uncomputed

    def map_qubit(self, name, index, promote=False):
        """Map a name to a qubit

        Args:
            promote (bool, optional): if True and if the qubit is an ancilla,
                remove from the ancilla set
        """
        if isinstance(name, Symbol):
            name = name.name

        # if name in self.qubit_map:
        #     raise Exception(f'Name "{name}" already mapped (to {self.qubit_map[name]})')

        if promote and index in self.ancilla_lst:
            self.ancilla_lst.remove(index)

        self[name] = index

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

        qs = set()
        for q in qubits:
            if q in qs:
                raise Exception(f"duplicate qubit in gate append: {gate_name} {qubits}")
            qs.add(q)

        self.gates.append((gate_name, qubits))
        self.gates_computed.append((gate_name, qubits))

    def barrier(self, label=None):
        """Add a barrier to the circuit"""
        self.gates.append(("bar", label))

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

    def mcx(self, wl: List[int], target):
        """Multi CX gate"""
        target = self[target]
        wl = list(map(lambda w: self[w], wl))
        self.append("mcx", wl + [target])

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
            elif g == "mcx":
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
            elif g == "mcx":
                qc.mcx(w[0:-1], w[-1])
            elif g == "bar" and mode != "gate":
                qc.barrier(label=w)
            elif g == "fredkin":
                qc.fredkin(w[0], w[1], w[2])

        if mode == "gate":
            qc.remove_final_measurements()
            gate = qc.to_gate()
            gate.name = self.name
            return gate
        elif mode == "circuit":
            return qc
        else:
            raise Exception(f"Uknown export mode: {mode}")

    def __qasm_export(self, mode: Literal["circuit", "gate"]):
        gate_qasm = f"gate {self.name} "
        gate_qasm += " ".join(self.qubit_map.keys())
        gate_qasm += " {\n"
        for x in self.gates:
            qbs = list(map(lambda gq: self.get_key_by_index(gq), x[1]))
            gate_qasm += f'\t{x[0]} {" ".join(qbs)}\n'
        gate_qasm += "}\n\n"

        if mode == "gate":
            return gate_qasm

        qasm = "OPENQASM 3.0;\n\n"
        qasm += gate_qasm

        return qasm

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
        elif framework == "qasm":
            return self.__qasm_export(mode)
        else:
            raise Exception(f"Framework {framework} not supported")

    def draw(self):
        qc = self.export("circuit", "qiskit")
        print(qc.draw("text"))
