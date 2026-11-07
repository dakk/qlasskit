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

from typing import Dict, List

from sympy.logic.boolalg import Boolean


class ExpQMap:
    """Mapping between boolexp and qubit and vice-versa"""

    exp_map: Dict[Boolean, int]

    def __init__(self):
        self.exp_map = {}

    def __contains__(self, exp: Boolean) -> bool:
        return exp in self.exp_map

    def __getitem__(self, exp: Boolean) -> int:
        return self.exp_map[exp]

    def __setitem__(self, exp: Boolean, qubit: int):
        self.remove([qubit])
        self.exp_map[exp] = qubit

    def remove(self, qubits: List[int]) -> None:
        """Remove qubits from the mapping"""
        todel = []
        for exp in self.exp_map.keys():
            if self.exp_map[exp] in qubits:
                todel.append(exp)

        for exp in todel:
            del self.exp_map[exp]
