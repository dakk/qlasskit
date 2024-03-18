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

from typing import List, Tuple

from sympy import And, Not, Symbol, Xor

from ..ast2logic.typing import BoolExpList
from ..qcircuit import QCircuit, gates


class DecompilerException(Exception):
    pass


class DecompiledSection:
    def __init__(self, gates, exps, sec_index):
        self.gates = gates
        self.expressions: BoolExpList = exps
        self.index: Tuple[int, int] = sec_index

    def __repr__(self):
        s = f"DecompiledResult[{self.index}](\n\t"
        s += ", ".join(map(str, self.gates))
        s += "\n\t" + ", ".join(map(str, self.expressions))
        s += "\n)"
        return s


class DecompilerResults:
    def __init__(self, sections=[]):
        self.sections: List[DecompiledSection] = []

    def __repr__(self):
        s = "DecompiledResults["

        for sec in self.sections:
            s += "\n\t("
            s += f"\n\t\t{sec.index}"
            s += "\n\t\t" + ", ".join(map(str, sec.gates))
            s += "\n\t\t" + ", ".join(map(str, sec.expressions))
            s += "\n\t)"

        s += "\n]"
        return s

    def __getitem__(self, i: int):
        return self.sections[i]

    def __len__(self):
        return len(self.sections)

    def __iter__(self):
        return self.sections.__iter__()

    def append(self, section: DecompiledSection):
        self.sections.append(section)


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
                exps[wn[2]] = Xor(And(exps[wn[0]], exps[wn[1]]), exps[wn[2]])
            elif isinstance(g, gates.MCX):
                exps[wn[-1]] = Xor(And(*[exps[ww] for ww in wn[0:-1]]), exps[wn[-1]])
            elif issubclass(g.__class__, gates.NopGate):
                continue
            else:
                raise Exception(f"Gate not handled for decompilation: {g.__name__}")

        exps_l = list(filter(lambda e: e[0] != e[1], exps.items()))
        return exps_l

    def decompile(self, qc: QCircuit) -> DecompilerResults:
        """Decompile a quantum circuit, searching for circuit sections that apply transformations
        on the z-basis on the same qubits, and return boolean expressions representing them
        """
        results = DecompilerResults()
        current_section = []
        current_section_start_index = None
        # current_section_qb = []  # TODO: populate this
        qc = qc.copy(True)

        i = 0
        for g, w, p in qc.gates + [(None, [0], None)]:
            if any(isinstance(g, zb_g) for zb_g in ZB_GATES):
                if current_section_start_index is None:
                    current_section_start_index = i
                current_section.append((g, w, p))
            elif issubclass(g.__class__, gates.NopGate):
                pass
            elif len(current_section) > 0:
                end = i
                if issubclass(qc.gates[i - 1][0].__class__, gates.NopGate):
                    end -= 1

                exps = self.__exps_of_section(qc, current_section)
                res = DecompiledSection(
                    current_section, exps, (current_section_start_index, end)
                )
                results.append(res)
                current_section = []
                current_section_start_index = None
            else:
                current_section = []

            i += 1

        return results
