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

from typing import List, Union

from .gates import CCX, CX, MCX, MCtrl, QGate, X
from .qcircuit import QCircuit


class GateNotSimulableException(Exception):
    def __init__(self, g: QGate):
        super(GateNotSimulableException, self).__init__(
            f"Gate not simulable by CNotSim: {g}"
        )


class CNotSim:
    """A dummy simulator for X, CX, CCX, MCX circuits"""

    def simulate(  # noqa: C901
        self,
        qc: QCircuit,
        initialize: List[bool] = [],
        to_measure: List[Union[int, str]] = [],
    ) -> List[bool]:
        """Simulate a quantum circuit qc

        Args:
            initialize (List[bool], optional): list of initializer for the qubits
            to_measure (List[int], optional): list of qubits to measure; measure all
                if None.
        """
        qubits = [False] * qc.num_qubits

        for i, x in enumerate(initialize):
            qubits[i] = x

        for g, w, p in qc.gates:
            if isinstance(g, X):
                qubits[w[0]] = not qubits[w[0]]
            elif (
                isinstance(g, CX)
                or isinstance(g, CCX)
                or isinstance(g, MCX)
                or (isinstance(g, MCtrl) and isinstance(g.gate, X))
            ):
                if all([qubits[x] for x in w[0:-1]]):
                    qubits[w[-1]] = not qubits[w[-1]]
            else:
                raise GateNotSimulableException(g)

        if len(to_measure) == 0:
            return qubits

        measured = []
        for q in to_measure:
            measured.append(qubits[qc[q]])
        return measured
