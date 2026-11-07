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

from typing import List, Tuple, Union

from sympy import Symbol
from sympy.logic.boolalg import Boolean

from ..types import TType


class Arg:
    def __init__(self, name: str, ttype: TType, bitvec: List[str]):
        self.name = name
        self.ttype = ttype
        self.bitvec = bitvec

    def __repr__(self) -> str:
        return f"{self.name} - {self.ttype} - [{', '.join(self.bitvec)}]"

    def __len__(self) -> int:
        return len(self.bitvec)

    def to_exp(self) -> Union[Symbol, List[Symbol]]:
        if len(self) > 1:
            return list(map(Symbol, self.bitvec))
        return Symbol(self.bitvec[0])


Args = List[Arg]
BoolExpList = List[Tuple[Symbol, Boolean]]
LogicFun = Tuple[str, Args, Arg, BoolExpList]
