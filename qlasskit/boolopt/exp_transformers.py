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

from sympy.logic import And, Not, Or, Xor

from . import SympyTransformer


class remove_ITE(SympyTransformer):
    def visit_ITE(self, expr):
        c = self.visit(expr.args[0])
        return self.visit(
            Or(
                And(c, self.visit(expr.args[1])),
                And(Not(c), self.visit(expr.args[2])),
            )
        )


class remove_Implies(SympyTransformer):
    def visit_Implies(self, expr):
        return self.visit(Or(Not(self.visit(expr.args[0])), self.visit(expr.args[1])))


class transform_or2xor(SympyTransformer):
    # Or(And(a,b), And(!a,!b)) = !Xor(a,b)
    def visit_Or(self, expr):
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
    def visit_Or(self, expr):
        return Not(And(*[Not(self.visit(e)) for e in expr.args]))
