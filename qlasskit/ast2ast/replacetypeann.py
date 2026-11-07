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
import copy
from typing import Union


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
