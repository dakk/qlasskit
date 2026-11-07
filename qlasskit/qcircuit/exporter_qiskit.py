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


class QiskitExporter(QCircuitExporter):
    def export(self, _selfqc, mode: Literal["circuit", "gate"]):  # noqa: C901
        from qiskit import QuantumCircuit
        from qiskit.circuit.library.standard_gates import ZGate

        qc = QuantumCircuit(_selfqc.num_qubits, 0)

        for g, w, p in _selfqc.gates:
            g_name = g.__class__.__name__.lower()

            if isinstance(g, gates.MCX) or (
                isinstance(g, gates.MCtrl) and isinstance(g.gate, gates.X)
            ):
                qc.mcx(w[0:-1], w[-1])
            elif isinstance(g, gates.MCtrl) and isinstance(g.gate, gates.Z):
                zg = ZGate().control(len(w[0:-1]))
                qc.append(zg, w)

            elif isinstance(g, gates.Barrier) and mode != "gate":
                qc.barrier(label=p)

            elif issubclass(g.__class__, gates.NopGate):
                pass

            elif hasattr(qc, g_name):
                if p:
                    getattr(qc, g_name)(p, *w)
                else:
                    getattr(qc, g_name)(*w)

            else:
                raise Exception(f"Gate not handled for qiskit exporter: {g_name}")

        if mode == "gate":
            qc.remove_final_measurements()
            gate = qc.to_gate()

            gate.name = _selfqc.name

            if hasattr(QuantumCircuit, _selfqc.name):
                gate.name += "_"

            return gate
        elif mode == "circuit":
            return qc
        else:
            raise Exception(f"Uknown export mode: {mode}")
