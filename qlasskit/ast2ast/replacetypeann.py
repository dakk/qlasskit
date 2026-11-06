# Copyright 2023-2025 Davide Gessa

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
