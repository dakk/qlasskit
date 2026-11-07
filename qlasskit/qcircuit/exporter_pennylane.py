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
