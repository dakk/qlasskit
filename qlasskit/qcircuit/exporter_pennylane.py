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

from typing import Literal

from . import gates
from .exporter import QCircuitExporter


class PennyLaneExporter(QCircuitExporter):
    def export(self, _selfqc, mode: Literal["circuit", "gate"]):  # noqa: C901
        import pennylane as qml

        ops = []

        for g, w, p in _selfqc.gates:
            g_name = g.__class__.__name__

            gate_mapping = {
                "CX": "CNOT",
                "CCX": "Toffoli",
                "H": "Hadamard",
                "X": "PauliX",
            }
            g_name = gate_mapping[g_name] if g_name in gate_mapping else g_name

            if isinstance(g, gates.MCX) or (
                isinstance(g, gates.MCtrl) and isinstance(g.gate, gates.X)
            ):
                if len(w) == 2:
                    ops.append(qml.CNOT(wires=w))
                elif len(w) == 3:
                    ops.append(qml.Toffoli(wires=w))
                else:
                    ops.append(
                        qml.ControlledQubitUnitary(
                            U=qml.PauliX, control_wires=w[0:-1], wires=[w[-1]]
                        )
                    )

            elif isinstance(g, gates.MCtrl) and isinstance(g.gate, gates.Z):
                ops.append(qml.CZ(wires=w))

            elif isinstance(g, gates.Swap):
                ops.append(qml.SWAP(wires=w))

            elif isinstance(g, gates.CP):
                ops.append(qml.CPhase(p, wires=w))

            elif issubclass(g.__class__, gates.NopGate):
                pass

            elif hasattr(qml, g_name):
                ops.append(getattr(qml, g_name)(wires=w))

            else:
                raise Exception(f"Gate not handled for pennylane exporter: {g_name}")

        return qml.tape.QuantumTape(ops)
