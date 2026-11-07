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

import math
from typing import Literal

from . import gates
from .exporter import QCircuitExporter


class CirqExporter(QCircuitExporter):
    def export(self, _selfqc, mode: Literal["circuit", "gate"]):  # noqa: C901
        import cirq

        if mode == "gate":

            class ExportedGate(cirq.Gate):  # type: ignore
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
                            yield gg(*(qubits[i] for i in w))

                        elif isinstance(g, gates.MCtrl) and isinstance(g.gate, gates.Z):
                            gg = cirq.ControlledGate(
                                sub_gate=cirq.Z, num_controls=len(w) - 1
                            )
                            yield gg(*(qubits[i] for i in w))

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
