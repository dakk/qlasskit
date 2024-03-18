# Copyright 2023-2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License..

from typing import Dict, List

from sympy.logic.boolalg import Boolean


class ExpQMap:
    """Mapping between boolexp and qubit and vice-versa"""

    def __init__(self):
        self.exp_map: Dict[Boolean, int] = {}

    def __contains__(self, exp):
        return exp in self.exp_map

    def __getitem__(self, exp):
        return self.exp_map[exp]

    def __setitem__(self, exp, qubit):
        self.remove([qubit])
        self.exp_map[exp] = qubit

    def remove(self, qubits: List[int]):
        """Remove qubits from the mapping"""
        todel = []
        for exp in self.exp_map.keys():
            if self.exp_map[exp] in qubits:
                todel.append(exp)

        for exp in todel:
            del self.exp_map[exp]
