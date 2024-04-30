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

from typing import Any, Dict, List, Optional

from .qcircuit import QCircuit, SupportedFramework


def reindex(idx: int, qb_l: List[int]):
    """Reindex a list of qubit `qb_l` to another location `idx`"""
    return list(map(lambda i: i + idx, qb_l))


class QCircuitWrapper:
    """Wrapper interface for a class containing a qcircuit"""

    _qcircuit: QCircuit

    def __init__(self):
        pass

    @property
    def num_qubits(self):
        return self._qcircuit.num_qubits

    @property
    def num_gates(self):
        return self._qcircuit.num_gates

    @property
    def input_qubits(self) -> List[int]:
        """Returns the list of input qubits"""
        raise Exception("Abstract")

    @property
    def output_qubits(self) -> List[int]:
        """Returns the list of output qubits"""
        raise Exception("Abstract")

    @property
    def qubits(self) -> List[int]:
        """Returns all the qubits of the circuit"""
        return list(range(self.num_qubits))

    @property
    def input_size(self) -> int:
        return len(self.input_qubits)

    @property
    def output_size(self) -> int:
        return len(self.output_qubits)

    def encode_input(self, *qvals):
        raise Exception("Abstract")

    def decode_output(self, istr):
        raise Exception("Abstract")

    def decode_counts(
        self, counts: Dict[str, int], discard_lower: Optional[int] = None
    ) -> Dict[Any, int]:
        """Decode data from a circuit counts dict"""
        outcomes = [(self.decode_output(e), c) for (e, c) in counts.items()]
        int_counts: Dict[Any, int] = {}
        for e, c in outcomes:
            if e in int_counts:
                int_counts[e] += c
            else:
                int_counts[e] = c

        if discard_lower:
            int_counts = dict(
                filter(lambda el: el[1] >= discard_lower, int_counts.items())
            )

        return int_counts

    def circuit(self):
        return self._qcircuit

    def gate(self, framework: SupportedFramework = "qiskit"):
        """Returns the gate for a specific framework"""
        return self._qcircuit.export(mode="gate", framework=framework)

    def export(self, framework: SupportedFramework = "qiskit") -> Any:
        """Export the circuit to a supported framework"""
        return self._qcircuit.export(mode="circuit", framework=framework)

    def draw(self):
        return self._qcircuit.draw()
