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

from sympy import Function
from sympy.logic.boolalg import Boolean


class QuantumBooleanGate(Function, Boolean):  # type: ignore
    # TODO: add an eval method to be able to simplify H(H(a)) => a

    def build(name: str):
        return type(name, (QuantumBooleanGate,), {})


class Q:
    """An identity wrapper for python"""

    def H(*args):
        return args

    def Z(*args):
        return args

    def Y(*args):
        return args

    def X(*args):
        return args

    def T(*args):
        return args

    def S(*args):
        return args

    def CX(*args):
        return args

    def MCX(*args):
        return args
