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

    def visit_Compare(self, node: ast.Compare):
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

    def visit_UnaryOp(self, node: ast.UnaryOp):
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

    def visit_BinOp(self, node: ast.BinOp):
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

    def visit_Call(self, node: ast.Call):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.builtin_funcs:

            def arg_tr(arg):
                if isinstance(arg, ast.Tuple) or isinstance(arg, ast.List):
                    elts = [self.visit(elt) for elt in arg.elts]
                    if all(isinstance(elt, ast.Constant) for elt in elts):
                        return ast.Constant([elt.value for elt in elts])  # type: ignore

                return arg

            args = list(map(arg_tr, node.args))

            if all(isinstance(arg, ast.Constant) for arg in args):
                func = self.builtin_funcs[node.func.id]
                args = [arg.value for arg in args]
                return ast.Constant(func(*args))  # type: ignore
        return node

    def visit_Subscript(self, node: ast.Subscript):
        self.generic_visit(node)
        if isinstance(node.value, ast.List) and isinstance(node.slice, ast.Constant):
            if all(isinstance(elt, ast.Constant) for elt in node.value.elts):
                try:
                    return node.value.elts[node.slice.value]  # type: ignore
                except IndexError:
                    pass
        return node

    def visit_If(self, node: ast.If):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            if node.test.value:
                return node.body
            else:
                return node.orelse
        return node

    def visit_IfExp(self, node: ast.IfExp):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else node.orelse
        return node
