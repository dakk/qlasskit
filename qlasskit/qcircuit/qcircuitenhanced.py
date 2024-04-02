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

import copy
from typing import List, Union

from sympy import Symbol

from . import gates
from .qcircuit import QCircuit


class QCircuitEnhanced(QCircuit):
    def __init__(self, num_qubits=0, name="qc", native=None):
        super().__init__(num_qubits, name, native)

        self.ancilla_lst = set()
        self.free_ancilla_lst = set()
        self.marked_ancillas = set()

    def map_qubit(self, name: Union[str, Symbol], index: int, promote=False):
        """Map a name to a qubit

        Args:
            name (Union[str, Symbol]): name of the qubit
            index (int): index of the qubit
            promote (bool, optional): if True and if the qubit is an ancilla,
                remove from the ancilla set
        """
        if isinstance(name, Symbol):
            name = name.name

        # if name in self.qubit_map:
        #     raise Exception(f'Name "{name}" already mapped (to {self.qubit_map[name]})')

        if promote and index in self.ancilla_lst:
            self.ancilla_lst.remove(index)

            # Remove the old name if present
            try:
                del self[self.get_key_by_index(index)]
            except:
                pass

        self[name] = index

    def remove_identities(self):
        """Remove identities from the circuit"""
        result: List[gates.AppliedGate] = []
        i = 0
        len_g = len(self.gates)  # type: ignore
        while i < len_g:
            if i < (len_g - 1) and self.gates[i] == self.gates[i + 1]:  # type: ignore
                if isinstance(result[-1][0], gates.Barrier):
                    result.pop()
                i += 2
            elif (
                i < (len_g - 2)
                and self.gates[i] == self.gates[i + 2]  # type: ignore
                and isinstance(self.gates[i + 1][0], gates.Barrier)  # type: ignore
            ):
                if isinstance(result[-1][0], gates.Barrier):
                    result.pop()
                i += 3
            else:
                result.append(self.gates[i])  # type: ignore
                i += 1

        self.gates = result

    def add_ancilla(self, name=None, is_free=True):
        """Add an ancilla qubit"""
        i = self.add_qubit(name if name else f"anc_{len(self.ancilla_lst)}")
        self.ancilla_lst.add(i)
        if is_free:
            self.free_ancilla_lst.add(i)
        return i

    def get_free_ancilla(self):
        """Get the first free ancilla available"""
        if len(self.free_ancilla_lst) == 0:
            anc = self.add_ancilla(is_free=False)
        else:
            anc = self.free_ancilla_lst.pop()

        return anc

    def mark_ancilla(self, w):
        """Mark an ancilla for uncomputing"""
        if w in self.ancilla_lst:
            self.marked_ancillas.add(w)

    def uncompute_all(self, keep: List[Union[Symbol, int]] = []):
        """Uncompute the whole circuit expect for the keep (symbols or qubit)"""
        # TODO: replace with + invert(keep)
        scopy = copy.deepcopy(self.gates)
        uncomputed = set()

        for g, qbs, p in reversed(scopy):
            if (
                issubclass(g.__class__, gates.NopGate)
                or qbs[-1] in keep
                or qbs[-1] in self.free_ancilla_lst
            ):
                continue
            uncomputed.add(qbs[-1])

            if qbs[-1] in self.ancilla_lst:
                self.free_ancilla_lst.add(qbs[-1])

            self.append(g, qbs, p)

        return uncomputed

    def uncompute(self, to_mark=[]):
        """Uncompute all the marked ancillas plus the to_mark list"""
        [self.mark_ancilla(x) for x in to_mark]

        if len(self.marked_ancillas) == 0:
            return []

        uncomputed = set()
        new_gates_comp = []

        for g, ws, p in reversed(self.gates_computed):  # type: ignore
            if ws[-1] in self.marked_ancillas:
                uncomputed.add(ws[-1])
                self.append(g, ws, p)
            else:
                new_gates_comp.append((g, ws, p))

        for x in self.marked_ancillas:
            self.free_ancilla_lst.add(x)
        self.marked_ancillas = self.marked_ancillas - uncomputed
        self.gates_computed = new_gates_comp[::-1]

        return uncomputed
