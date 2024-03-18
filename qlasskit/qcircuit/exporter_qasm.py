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


class QasmExporter(QCircuitExporter):
    def __init__(self, version=3):
        self.version = version

    def export_v3(self, _selfqc, mode: Literal["circuit", "gate"]):
        gate_qasm = f"gate {_selfqc.name} "
        gate_qasm += " ".join(_selfqc.qubit_map.keys())
        gate_qasm += " {\n"
        for g, ws, p in _selfqc.gates:
            if issubclass(g.__class__, gates.NopGate):
                continue

            qbs = list(map(lambda gq: _selfqc.get_key_by_index(gq), ws))
            if p:
                gate_qasm += f'\t{g.__name__.lower()}({p:.2f}) {" ".join(qbs)}\n'
            else:
                gate_qasm += f'\t{g.__name__.lower()} {" ".join(qbs)}\n'
        gate_qasm += "}\n\n"

        if mode == "gate":
            return gate_qasm

        qasm = "OPENQASM 3.0;\n\n"
        qasm += gate_qasm
        qasm += (
            _selfqc.name
            + " "
            + ",".join(map(lambda c: f"q[{c}]", range(_selfqc.num_qubits)))
            + ";\n"
        )

        return qasm

    def export_v2(self, _selfqc, mode: Literal["circuit", "gate"]):
        gate_qasm = f"gate {_selfqc.name} "
        gate_qasm += " ".join(_selfqc.qubit_map.keys())
        gate_qasm += " {\n"
        for g, ws, p in _selfqc.gates:
            if issubclass(g.__class__, gates.NopGate):
                continue

            qbs = list(map(lambda gq: _selfqc.get_key_by_index(gq), ws))
            if p:
                gate_qasm += f'\t{g.__name__.lower()}({p:.2f}) {" ".join(qbs)}\n'
            else:
                gate_qasm += f'\t{g.__name__.lower()} {" ".join(qbs)}\n'
        gate_qasm += "}\n\n"

        if mode == "gate":
            return gate_qasm

        qasm = "OPENQASM 2.0;\n\n"
        qasm += 'include "qelib1.inc";\n\n'
        qasm += "qreg q[" + str(_selfqc.num_qubits) + "];\n"
        qasm += gate_qasm
        qasm += (
            _selfqc.name
            + " "
            + ",".join(map(lambda c: f"q[{c}]", range(_selfqc.num_qubits)))
            + ";\n"
        )

        return qasm

    def export(self, _selfqc, mode: Literal["circuit", "gate"]):
        if self.version == 3:
            return self.export_v3(_selfqc, mode)
        else:
            return self.export_v2(_selfqc, mode)
