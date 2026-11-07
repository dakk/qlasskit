# Copyright (C) 2023-2026 Davide Gessa
# This file is part of Qlasskit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Any, Dict, List, Optional

from .qcircuit import QCircuit, SupportedFramework


def reindex(idx: int, qb_l: List[int]) -> List[int]:
    """Reindex a list of qubit `qb_l` to another location `idx`"""
    return list(map(lambda i: i + idx, qb_l))


class QCircuitWrapper:
    """Wrapper interface for a class containing a qcircuit"""

    _qcircuit: QCircuit

    @property
    def num_qubits(self) -> int:
        return self._qcircuit.num_qubits

    @property
    def num_gates(self) -> int:
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

    def circuit(self) -> QCircuit:
        return self._qcircuit

    def gate(self, framework: SupportedFramework = "qiskit"):
        """Returns the gate for a specific framework"""
        return self._qcircuit.export(mode="gate", framework=framework)

    def export(self, framework: SupportedFramework = "qiskit") -> Any:
        """Export the circuit to a supported framework"""
        return self._qcircuit.export(mode="circuit", framework=framework)

    def draw(self):
        return self._qcircuit.draw()
