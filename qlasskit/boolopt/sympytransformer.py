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

from sympy.logic import ITE, And, Implies, Not, Or, Xor
from sympy.logic.boolalg import Boolean


class SympyTransformer:
    def visit(self, e: Boolean) -> Boolean:
        if isinstance(e, And):
            return self.visit_And(e)
        elif isinstance(e, Or):
            return self.visit_Or(e)
        elif isinstance(e, Not):
            return self.visit_Not(e)
        elif isinstance(e, Implies):
            return self.visit_Implies(e)
        elif isinstance(e, ITE):
            return self.visit_ITE(e)
        elif isinstance(e, Xor):
            return self.visit_Xor(e)
        else:
            return e

    def visit_And(self, e: Boolean) -> Boolean:
        return And(*[self.visit(a) for a in e.args])

    def visit_Or(self, e: Boolean) -> Boolean:
        return Or(*[self.visit(a) for a in e.args])

    def visit_Not(self, e: Boolean) -> Boolean:
        return Not(self.visit(e.args[0]))

    def visit_ITE(self, e: Boolean) -> Boolean:
        return ITE(*[self.visit(a) for a in e.args])

    def visit_Implies(self, e: Boolean) -> Boolean:
        return Implies(*[self.visit(a) for a in e.args])

    def visit_Xor(self, e: Boolean) -> Boolean:
        return Xor(*[self.visit(a) for a in e.args])
