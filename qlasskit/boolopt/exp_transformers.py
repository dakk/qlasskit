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

from sympy import Symbol
from sympy.logic import And, Not, Or, Xor
from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue

from . import SympyTransformer

DISABLE_OR = False


class remove_ITE(SympyTransformer):
    def visit_ITE(self, expr: Boolean) -> Boolean:
        c = self.visit(expr.args[0])
        return self.visit(
            Or(
                And(c, self.visit(expr.args[1])),
                And(Not(c), self.visit(expr.args[2])),
            )
        )


class remove_Implies(SympyTransformer):
    def visit_Implies(self, expr: Boolean) -> Boolean:
        return self.visit(Or(Not(self.visit(expr.args[0])), self.visit(expr.args[1])))


class transform_or2xor(SympyTransformer):
    # Or(And(a,b), And(!a,!b)) = !Xor(a,b)
    def visit_Or(self, expr: Boolean) -> Boolean:
        if (
            len(expr.args) == 2
            and isinstance(expr.args[0], And)
            and isinstance(expr.args[1], And)
            and (
                (
                    expr.args[1].args[0] == Not(expr.args[0].args[0])
                    and expr.args[1].args[1] == Not(expr.args[0].args[1])
                )
                or (
                    Not(expr.args[1].args[0]) == expr.args[0].args[0]
                    and Not(expr.args[1].args[1]) == expr.args[0].args[1]
                )
            )
        ):
            a = self.visit(expr.args[0].args[0])
            b = self.visit(expr.args[0].args[1])
            return Not(Xor(a, b))
        else:
            return super().visit_Or(expr)


class transform_or2and(SympyTransformer):
    def visit_Or(self, expr: Boolean) -> Boolean:
        if len(expr.args) > 2 or DISABLE_OR:
            return Not(And(*[Not(self.visit(e)) for e in expr.args]))
        return expr


class remove_obvious_expr(SympyTransformer):
    def visit_Not(self, expr: Boolean) -> Boolean:
        if isinstance(expr.args[0], Not):
            return expr.args[0].args[0]
        return expr

    def visit_And(self, expr: Boolean) -> Boolean:
        if len(expr.args) == 2 and (
            (
                isinstance(expr.args[0], Symbol)
                and isinstance(expr.args[1], Not)
                and (expr.args[0] == expr.args[1].args[0])
            )
            or (
                isinstance(expr.args[0], Not)
                and isinstance(expr.args[1], Symbol)
                and (expr.args[1] == expr.args[0].args[0])
            )
        ):
            return BooleanFalse()

        return expr

    def visit_Or(self, expr: Boolean) -> Boolean:
        if len(expr.args) == 2 and (
            (
                isinstance(expr.args[0], Symbol)
                and isinstance(expr.args[1], Not)
                and (expr.args[0] == expr.args[1].args[0])
            )
            or (
                isinstance(expr.args[0], Not)
                and isinstance(expr.args[1], Symbol)
                and (expr.args[1] == expr.args[0].args[0])
            )
        ):
            return BooleanTrue()

        return expr
