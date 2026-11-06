# Copyright 2023-2026 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
