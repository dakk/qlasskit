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

from typing import List, Union

from .gates import CCX, CX, MCX, MCtrl, X
from .qcircuit import QCircuit


class GateNotSimulableException(Exception):
    def __init__(self, g):
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
