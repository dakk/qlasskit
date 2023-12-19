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

from typing import Literal

from sympy.physics.quantum.gate import CNOT, CGate, H, X, XGate
from sympy.physics.quantum.qubit import Qubit

from . import gates
from .exporter import QCircuitExporter


def mcx(w):
    return CGate(tuple(w[0:-1]), XGate(w[-1]))


def toffoli(q0, q1, q2):
    return CGate((q0, q1), XGate(q2))


class SympyExporter(QCircuitExporter):
    def export(self, _selfqc, mode: Literal["circuit", "gate"]):
        qstate = Qubit("0" * _selfqc.num_qubits)

        for g, w, p in _selfqc.gates:
            ga = None
            if isinstance(g, gates.X):
                ga = X(w[0])
            elif isinstance(g, gates.H):
                ga = H(w[0])
            elif isinstance(g, gates.CX):
                ga = CNOT(w[0], w[1])
            elif isinstance(g, gates.CCX) or isinstance(g, gates.MCX):
                ga = mcx(w)
            elif isinstance(g, gates.Barrier) and mode != "gate":
                pass
            elif isinstance(g, gates.NopGate):
                pass
            else:
                raise Exception("not handled")

            if ga:
                qstate = ga * qstate

        return qstate
