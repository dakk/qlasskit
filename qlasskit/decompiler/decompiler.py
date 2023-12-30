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

from typing import List

from sympy import And, Not, Symbol, Xor

from ..ast2logic.typing import BoolExpList
from ..qcircuit import QCircuit, gates


class DecompilerException(Exception):
    pass


class DecompilerResult:
    def __init__(self, section, exps):
        self.section = section
        self.expressions: BoolExpList = exps

    def __repr__(self):
        s = "DecompiledResult(\n\t"
        s += ", ".join(map(str, self.section))
        s += "\n\t" + ", ".join(map(str, self.expressions))
        s += "\n)"
        return s


DecompilerResults = List[DecompilerResult]

ZB_GATES = [
    gates.I,
    gates.X,
    gates.MCX,
    gates.CCX,
    gates.CX,
    # gates.Swap
]


class Decompiler:
    def __init__(self):
        pass

    def __exps_of_section(self, qc: QCircuit, section):
        exps = {}

        def check_or_add(w):
            names = []
            for wi in w:
                qci = qc[wi]
                qcn = Symbol(qc.get_key_by_index(qci))

                if qcn not in exps:
                    exps[qcn] = qcn
                names.append(qcn)
            return names

        for g, w, p in section:
            wn = check_or_add(w)
            if isinstance(g, gates.X):
                exps[wn[0]] = Not(exps[wn[0]])
            elif isinstance(g, gates.CX):
                exps[wn[1]] = Xor(exps[wn[0]], exps[wn[1]])
            elif isinstance(g, gates.CCX):
                exps[wn[2]] = And(exps[wn[0]], exps[wn[1]], exps[wn[2]])
            elif isinstance(g, gates.MCX):
                exps[wn[-1]] = And(*[exps[ww] for ww in wn[0:-1]])
            elif issubclass(g.__class__, gates.NopGate):
                continue
            else:
                raise Exception("Not handled", g)

        exps_l = list(filter(lambda e: e[0] != e[1], exps.items()))
        return exps_l

    def decompile(self, qc: QCircuit) -> DecompilerResults:
        """Decompile a quantum circuit, searching for circuit sections that apply transformations
        on the z-basis on the same qubits, and return boolean expressions representing them
        """
        results = []
        current_section = []
        for g, w, p in qc.gates + [(None, [0], None)]:
            if any(isinstance(g, zb_g) for zb_g in ZB_GATES) or issubclass(
                g.__class__, gates.NopGate
            ):
                current_section.append((g, w, p))
            elif len(current_section) > 0:
                exps = self.__exps_of_section(qc, current_section)
                res = DecompilerResult(current_section, exps)
                results.append(res)
                current_section = []
            else:
                current_section = []

        return results
