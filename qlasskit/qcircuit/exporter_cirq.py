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

import math
from typing import Literal

from . import gates
from .exporter import QCircuitExporter


class CirqExporter(QCircuitExporter):
    def export(self, _selfqc, mode: Literal["circuit", "gate"]):  # noqa: C901
        import cirq

        if mode == "gate":

            class ExportedGate(cirq.Gate):
                def init(self):
                    super(ExportedGate, self)

                def _num_qubits_(self):
                    return _selfqc.num_qubits

                def _decompose_(self, qubits):
                    for g, w, p in _selfqc.gates:
                        g_name = g.__class__.__name__

                        gate_mapping = {"CX": "CNOT", "CCX": "CCNOT"}
                        g_name = (
                            gate_mapping[g_name] if g_name in gate_mapping else g_name
                        )

                        if isinstance(g, gates.MCX) or (
                            isinstance(g, gates.MCtrl) and isinstance(g.gate, gates.X)
                        ):
                            gg = cirq.ControlledGate(
                                sub_gate=cirq.X, num_controls=len(w) - 1
                            )
                            yield gg(list(map(lambda wx: qubits[w], w)))

                        elif isinstance(g, gates.MCtrl) and isinstance(g.gate, gates.Z):
                            gg = cirq.ControlledGate(
                                sub_gate=cirq.Z, num_controls=len(w) - 1
                            )
                            yield gg(list(map(lambda wx: qubits[w], w)))

                        elif isinstance(g, gates.Swap):
                            yield cirq.SWAP(qubits[w[0]], qubits[w[1]])

                        elif isinstance(g, gates.CP):
                            cphase_gate = cirq.CZPowGate(exponent=p / math.pi)
                            yield cphase_gate(qubits[w[0]], qubits[w[1]])

                        elif hasattr(cirq, g_name):
                            yield getattr(cirq, g_name)(
                                *list(map(lambda x: qubits[x], w))
                            )

                        else:
                            raise Exception(
                                f"Gate not handled for cirq exporter: {g_name}"
                            )

                def _circuit_diagram_info_(self, args):
                    return [_selfqc.name] * self.num_qubits()

            ExportedGate.__name__ = _selfqc.name
            return ExportedGate
        elif mode == "circuit":
            circ = cirq.Circuit()
            qubits = cirq.LineQubit.range(_selfqc.num_qubits)

            gat = _selfqc.export("gate", "cirq")

            circ = cirq.Circuit(gat().on(*qubits))
            return circ

        else:
            raise Exception(f"Uknown export mode: {mode}")
