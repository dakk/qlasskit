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
"""AST preprocessing passes, applied before translate_ast: constant folding,
high-level type annotation replacement and multi-target assign expansion."""

import ast
import copy
import operator
from typing import Union


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


class TypeAnnotationsReplacer(ast.NodeTransformer):
    def visit_Subscript(self, ann: ast.Subscript):
        if not isinstance(ann.value, ast.Name) or not hasattr(ann.slice, "elts"):
            return ann

        if ann.value.id == "Tuple":
            _elts = ann.slice.elts
            _ituple = ast.Tuple(elts=[self.visit(el) for el in _elts])

            return ast.Subscript(
                value=ast.Name(id="Tuple", ctx=ast.Load()),
                slice=_ituple,
            )

        # Replace Qlist[T,n] with Tuple[(T,)*n]
        elif ann.value.id == "Qlist":
            _elts = ann.slice.elts
            _ituple = ast.Tuple(elts=[copy.deepcopy(_elts[0])] * _elts[1].value)

            return ast.Subscript(
                value=ast.Name(id="Tuple", ctx=ast.Load()),
                slice=_ituple,
            )

        # Replace Qmatrix[T,n,m] with Tuple[(Tuple[(T,)*m],)*n]
        elif ann.value.id == "Qmatrix":
            _elts = ann.slice.elts
            _ituple_row = ast.Tuple(elts=[copy.deepcopy(_elts[0])] * _elts[2].value)
            _ituple = ast.Tuple(elts=[copy.deepcopy(_ituple_row)] * _elts[1].value)

            return ast.Subscript(
                value=ast.Name(id="Tuple", ctx=ast.Load()),
                slice=_ituple,
            )

        return ann

    def visit_Name(self, ann: ast.Name):
        res_ann: Union[ast.Name, ast.Subscript]

        # Replace QintX with Qint[X]
        if ann.id[:4] == "Qint":
            res_ann = ast.Subscript(
                value=ast.Name(id="Qint", ctx=ast.Load()),
                slice=ast.Constant(value=int(ann.id[4:])),
            )

        # Replace QfixedX with Qfixed[X]
        elif ann.id[:6] == "Qfixed":
            res_ann = ast.Subscript(
                value=ast.Name(id="Qfixed", ctx=ast.Load()),
                slice=ast.Constant(value=int(ann.id[6:])),
            )

        else:
            res_ann = ann

        return res_ann


def _replace_types_annotations(ann, arg=None):
    """Replaces type annotations, translating high level types"""
    if ann is not None:
        ann = TypeAnnotationsReplacer().visit(ann)

    if arg is not None:
        arg.annotation = ann
        return arg
    else:
        return ann


class ReplaceTypeAnn(ast.NodeTransformer):
    def visit_AnnAssign(self, node: ast.AnnAssign):
        node.annotation = _replace_types_annotations(node.annotation)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        node.args.args = [
            _replace_types_annotations(x.annotation, arg=x) for x in node.args.args
        ]

        node.returns = _replace_types_annotations(node.returns)

        return node


class ReplaceMultiTargetAssign(ast.NodeTransformer):
    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) != 1 or not hasattr(node.targets[0], "elts"):
            return node

        # Transform multi-target assign to single target assigns
        if isinstance(node.value, ast.Name):
            return [
                self.visit(
                    ast.Assign(
                        targets=[ast.Name(id=node.targets[0].elts[i].id)],
                        value=ast.Subscript(
                            value=node.value, slice=ast.Constant(value=i)
                        ),
                    )
                )
                for i in range(len(node.targets[0].elts))
            ]

        _temptup = self.visit(
            ast.Assign(targets=[ast.Name(id="_temptup")], value=node.value)
        )

        single_assigns = [
            self.visit(
                ast.Assign(
                    targets=[ast.Name(id=node.targets[0].elts[i].id)],
                    value=ast.Subscript(
                        value=ast.Name(id="_temptup"), slice=ast.Constant(value=i)
                    ),
                )
            )
            for i in range(len(node.targets[0].elts))
        ]

        return [_temptup] + single_assigns


def preprocess_ast(a_tree: ast.AST) -> ast.AST:
    """Apply the preprocessing passes to the ast before translate_ast"""
    # Fold constants
    a_tree = ConstantFolder().visit(a_tree)

    # Replace Type Annotations
    a_tree = ReplaceTypeAnn().visit(a_tree)

    # Replace multi-target assign
    a_tree = ReplaceMultiTargetAssign().visit(a_tree)

    # Fold constants again
    a_tree = ConstantFolder().visit(a_tree)

    return a_tree
