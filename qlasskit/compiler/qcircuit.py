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
from typing import List


class QCircuit:
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.gates = []
        self.qubit_map = {}

    def add_qubit(self):
        self.num_qubits += 1
        return self.num_qubits - 1

    def append(self, gate_name: str, wires: List[int]):
        for x in wires:
            if x > self.num_qubits:
                raise Exception(f"Wire {x} not present")

        self.gates.append((gate_name, wires))

    def x(self, w):
        self.append(("x", [w]))

    def cx(self, w1, w2):
        self.append(("cx", [w1, w2]))

    def ccx(self, w1, w2, w3):
        self.append(("ccx", [w1, w2, w3]))

    def export(self, framework="qiskit"):
        pass
