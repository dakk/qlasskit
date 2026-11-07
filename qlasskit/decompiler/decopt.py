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

from typing import List, Optional

from sympy import Symbol
from sympy.logic.boolalg import And, Boolean, Not, Or, Xor, simplify_logic

from .. import QCircuit

# from ..boolopt import custom_simplify_logic
from ..compiler import SupportedCompiler, exprs_to_quantum
from . import Decompiler


# This differs from the bool_optimizer version
def custom_simplify_logic2(expr: Boolean) -> Boolean:
    if isinstance(expr, Xor):
        se = simplify_logic(expr)
        if isinstance(se, Xor) or isinstance(se, Not) or isinstance(se, Symbol):
            return se
        else:
            args = [custom_simplify_logic2(arg) for arg in expr.args]
            return type(expr)(*args)
    elif isinstance(expr, (And, Or, Not)):
        args = [custom_simplify_logic2(arg) for arg in expr.args]
        return type(expr)(*args)
    else:
        return simplify_logic(expr)


def circuit_boolean_optimizer(
    qc: QCircuit,
    compiler: SupportedCompiler = "internal",
    preserve: Optional[List[int]] = None,
) -> QCircuit:
    """Decompile the quantum circuit, simplify boolean sections, and recreate an
    optimized quantum circuit. If preserve is set, the given list of qubits are preserved,
    while others are initialized to False."""
    qc = qc.copy(True)
    dc = Decompiler().decompile(qc)
    qc_new = qc.copy(True)

    # Set not-preserved qubits to False
    emap = {}
    for i in range(qc.num_qubits) if preserve else []:
        if i in preserve:  # type: ignore
            continue
        emap[Symbol(f"q{i}")] = False

    for section in reversed(dc):
        n_exps = []

        # Get the involved qubit set
        section_qubits = set()
        for g, w, p in section.gates:
            for i in w:
                section_qubits.add(i)

        # Simplify expressions
        for s, e in section.expressions:
            e_symp = custom_simplify_logic2(e)
            # print(s, ":", e, "=>", e_symp)
            n_exps.append((s, e_symp.xreplace(emap)))

        # Create new circuit section using the compiler
        symbols = list(qc.qubit_map.keys())

        if preserve:
            symbols = list(map(lambda x: f"q{x}", preserve))

        qc_sec = exprs_to_quantum(exprs=n_exps, symbols=symbols, compiler=compiler)

        if (
            len(qc_sec.gates) > len(section.gates)
            or (qc_sec.used_qubits - section_qubits) != set()
        ):
            continue

        # Replace the circuit section with the new one
        qc_new.gates[section.index[0] : section.index[1]] = qc_sec.gates

    return qc_new
