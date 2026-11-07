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

from sympy.logic.boolalg import Boolean

from .. import QCircuit
from ..ast2logic.typing import Arg, Args, BoolExpList


class CompilerException(Exception):
    pass


class Compiler:
    def _symplify_exp(self, exp: Boolean):
        # exp = to_anf(exp, deep=False)
        return exp

    def compile(
        self, name: str, args: Args, returns: Arg, expr: BoolExpList, uncompute: bool
    ) -> QCircuit:
        raise Exception("abstract")
