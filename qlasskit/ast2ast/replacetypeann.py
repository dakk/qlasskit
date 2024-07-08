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
import copy


def _replace_types_annotations(ann, arg=None):
    """Replaces type annotations, translating high level types"""
    if (
        isinstance(ann, ast.Subscript)
        and isinstance(ann.value, ast.Name)
        and ann.value.id == "Tuple"
        and hasattr(ann.slice, "elts")
    ):
        _elts = ann.slice.elts
        _ituple = ast.Tuple(elts=[_replace_types_annotations(el) for el in _elts])

        ann = ast.Subscript(
            value=ast.Name(id="Tuple", ctx=ast.Load()),
            slice=_ituple,
        )

    # Replace QintX with Qint[X]
    if isinstance(ann, ast.Name) and ann.id[:4] == "Qint":
        ann = ast.Subscript(
            value=ast.Name(id="Qint", ctx=ast.Load()),
            slice=ast.Constant(value=int(ann.id[4:])),
        )

    # Replace QfixedX with Qfixed[X]
    if isinstance(ann, ast.Name) and ann.id[:6] == "Qfixed":
        ann = ast.Subscript(
            value=ast.Name(id="Qfixed", ctx=ast.Load()),
            slice=ast.Constant(value=int(ann.id[6:])),
        )

    # Replace Qlist[T,n] with Tuple[(T,)*n]
    if (
        isinstance(ann, ast.Subscript)
        and isinstance(ann.value, ast.Name)
        and ann.value.id == "Qlist"
        and hasattr(ann.slice, "elts")
    ):
        _elts = ann.slice.elts
        _ituple = ast.Tuple(elts=[copy.deepcopy(_elts[0])] * _elts[1].value)

        ann = ast.Subscript(
            value=ast.Name(id="Tuple", ctx=ast.Load()),
            slice=_ituple,
        )

    # Replace Qmatrix[T,n,m] with Tuple[(Tuple[(T,)*m],)*n]
    if (
        isinstance(ann, ast.Subscript)
        and isinstance(ann.value, ast.Name)
        and ann.value.id == "Qmatrix"
        and hasattr(ann.slice, "elts")
    ):
        _elts = ann.slice.elts
        _ituple_row = ast.Tuple(elts=[copy.deepcopy(_elts[0])] * _elts[2].value)
        _ituple = ast.Tuple(elts=[copy.deepcopy(_ituple_row)] * _elts[1].value)

        ann = ast.Subscript(
            value=ast.Name(id="Tuple", ctx=ast.Load()),
            slice=_ituple,
        )

    if arg is not None:
        arg.annotation = ann
        return arg
    else:
        return ann


class ReplaceTypeAnn(ast.NodeTransformer):
    def visit_AnnAssign(self, node):
        node.annotation = _replace_types_annotations(node.annotation)
        return node

    def visit_FunctionDef(self, node):
        node.args.args = [
            _replace_types_annotations(x.annotation, arg=x) for x in node.args.args
        ]

        node.returns = _replace_types_annotations(node.returns)

        return node
