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

import ast
import operator


class ConstantFolder(ast.NodeTransformer):
    def __init__(self):
        self.builtin_funcs = {
            "abs": abs,
            "len": len,
            "min": min,
            "max": max,
            "sum": sum,
            "any": any,
            "all": all,
            "chr": chr,
            "ord": ord,
            # "range": range, # This is handled differently
        }

    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1 and len(node.comparators) == 1:
            if isinstance(node.left, ast.Constant) and isinstance(
                node.comparators[0], ast.Constant
            ):
                op = {
                    ast.Eq: operator.eq,
                    ast.NotEq: operator.ne,
                    ast.Lt: operator.lt,
                    ast.LtE: operator.le,
                    ast.Gt: operator.gt,
                    ast.GtE: operator.ge,
                    ast.Is: operator.is_,
                    ast.IsNot: operator.is_not,
                    ast.In: lambda x, y: x in y,
                    ast.NotIn: lambda x, y: x not in y,
                }.get(type(node.ops[0]))
                if op:
                    result = op(node.left.value, node.comparators[0].value)
                    return ast.Constant(result)
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.operand, ast.Constant):
            op = {
                ast.UAdd: operator.pos,
                ast.USub: operator.neg,
                ast.Not: operator.not_,
                ast.Invert: operator.invert,
            }.get(type(node.op))
            if op:
                return ast.Constant(op(node.operand.value))  # type: ignore
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            op = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow,
                ast.LShift: operator.lshift,
                ast.RShift: operator.rshift,
                ast.BitOr: operator.or_,
                ast.BitXor: operator.xor,
                ast.BitAnd: operator.and_,
            }.get(type(node.op))
            if op:
                return ast.Constant(op(node.left.value, node.right.value))
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.builtin_funcs:

            def arg_tr(arg):
                if isinstance(arg, ast.Tuple) or isinstance(arg, ast.List):
                    elts = [self.visit(elt) for elt in arg.elts]
                    if all(isinstance(elt, ast.Constant) for elt in elts):
                        return ast.Constant([elt.value for elt in elts])

                return arg

            args = list(map(arg_tr, node.args))

            if all(isinstance(arg, ast.Constant) for arg in args):
                func = self.builtin_funcs[node.func.id]
                args = [arg.value for arg in args]
                return ast.Constant(func(*args))  # type: ignore
        return node

    def visit_Subscript(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.List) and isinstance(node.slice, ast.Constant):
            if all(isinstance(elt, ast.Constant) for elt in node.value.elts):
                try:
                    return node.value.elts[node.slice.value]
                except IndexError:
                    pass
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            if node.test.value:
                return node.body
            else:
                return node.orelse
        return node

    def visit_IfExp(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else node.orelse
        return node
