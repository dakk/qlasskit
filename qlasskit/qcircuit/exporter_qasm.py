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
