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
