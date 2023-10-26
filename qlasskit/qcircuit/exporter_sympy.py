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

from sympy.physics.quantum.gate import CNOT, H, T, X
from sympy.physics.quantum.qubit import Qubit

from . import gates
from .exporter import QCircuitExporter


class SympyExporter(QCircuitExporter):
    def export(self, _selfqc, mode: Literal["circuit", "gate"]):
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

        qstate = Qubit("0" * _selfqc.num_qubits)

        for g, w, p in _selfqc.gates:
            ga = None
            if isinstance(g, gates.X):
                ga = X(w[0])
            elif isinstance(g, gates.CX):
                ga = CNOT(w[0], w[1])
            elif isinstance(g, gates.CCX):
                raise Exception("Not implemented yet")
            elif isinstance(g, gates.MCX):
                raise Exception("Not implemented yet")
            elif g != "bar":
                raise Exception(f"not handled {g}")

            if ga:
                qstate = ga * qstate

        return qstate
