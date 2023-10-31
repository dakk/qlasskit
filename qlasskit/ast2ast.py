# Copyright 2023 Davide Gessa

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
import sys

from .ast2logic import flatten


class NameValReplacer(ast.NodeTransformer):
    def __init__(self, name_id, val):
        self.name_id = name_id
        self.val = val

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_Name(self, node):
        if node.id == self.name_id:
            return self.val

        return node


class ASTRewriter(ast.NodeTransformer):
    def __init__(self, env={}, ret=None):
        self.env = {}
        self.const = {}
        self.ret = None

    def __unroll_arg(self, arg):
        if isinstance(arg, ast.Tuple):
            return arg.elts
        elif isinstance(arg, ast.Name):
            if (
                arg.id in self.env
                and isinstance(self.env[arg.id], ast.Subscript)
                and self.env[arg.id].value.id == "Tuple"
            ):
                if sys.version_info < (3, 9):
                    _sval = self.env[arg.id].slice.value
                else:
                    _sval = self.env[arg.id].slice

                return [
                    ast.Subscript(
                        value=ast.Name(id=arg.id, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Constant(value=i, kind=None)),
                    )
                    for i in range(len(_sval.elts))
                ]
        return [arg]

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_Subscript(self, node):
        if sys.version_info < (3, 9):
            _sval = node.slice.value
        else:
            _sval = node.slice

        if (
            isinstance(node.slice, ast.Index)
            and isinstance(_sval, ast.Name)
            and _sval.id in self.const
        ):
            if sys.version_info < (3, 9):
                node.slice.value = self.const[_sval.id]
            else:
                node.slice = self.const[_sval.id]
        return node

    def visit_Name(self, node):
        if node.id[0:2] == "__":
            raise Exception("invalid name starting with __")

        return node

    def visit_List(self, node):
        return ast.Tuple(elts=[self.visit(el) for el in node.elts])

    def visit_FunctionDef(self, node):
        def _replace_types(ann, arg=None):
            # Replace Qlist[T,n] with Tuple[(T,)*3]
            if isinstance(ann, ast.Subscript) and ann.value.id == "Qlist":
                if sys.version_info < (3, 9):
                    _elts = ann.slice.value.elts
                else:
                    _elts = ann.slice.elts

                _ituple = ast.Tuple(elts=[copy.deepcopy(_elts[0])] * _elts[1].value)

                if sys.version_info < (3, 9):
                    _ituple = ast.Index(value=_ituple)

                ann = ast.Subscript(
                    value=ast.Name(id="Tuple", ctx=ast.Load()),
                    slice=_ituple,
                )

            if arg is not None:
                arg.annotation = ann
                return arg
            else:
                return ann

        node.args.args = [_replace_types(x.annotation, arg=x) for x in node.args.args]

        for x in node.args.args:
            self.env[x.arg] = x.annotation

        node.returns = _replace_types(node.returns)
        self.ret = node.returns

        return super().generic_visit(node)

    def visit_Assign(self, node):
        # Transform multi-target assign to single target assigns
        if len(node.targets) == 1 and hasattr(node.targets[0], "elts"):
            _temptup = self.visit(
                ast.Assign(targets=[ast.Name(id="_temptup")], value=node.value)
            )

            single_assigns = [
                self.visit(
                    ast.Assign(
                        targets=[ast.Name(id=node.targets[0].elts[i].id)],
                        value=ast.Subscript(
                            value=ast.Name(id="_temptup"),
                            slice=ast.Index(
                                value=ast.Constant(value=i), ctx=ast.Load()
                            ),
                        ),
                    )
                )
                for i in range(len(node.targets[0].elts))
            ]
            return [_temptup] + single_assigns

        target_0id = node.targets[0].id
        was_known = target_0id in self.env

        if isinstance(node.value, ast.Name) and node.value.id in self.env:
            self.env[target_0id] = self.env[node.value.id]
        elif isinstance(node.value, ast.Tuple) or isinstance(node.value, ast.List):
            self.env[target_0id] = self.visit(node.value)
        else:
            self.env[target_0id] = "Unknown"

        # TODO: support unrolling tuple
        # TODO: if value is not self referencing, we can skip this (ie: a = b + 1)

        # Reassigning an already present variable (use a temp variable)
        if was_known and not isinstance(node.value, ast.Constant):
            new_targ = ast.Name(id=f"__{target_0id}", ctx=ast.Load())

            return [
                ast.Assign(
                    targets=[new_targ],
                    value=self.visit(node.value),
                ),
                ast.Assign(
                    targets=node.targets,
                    value=new_targ,
                ),
            ]

        node.value = self.visit(node.value)
        return node

    def visit_AugAssign(self, node):
        """Translate AugAssign to Assign + BinOp (+=, -=, etc)"""
        # Reassigning an already present variable (use a temp variable)
        # if node.target.id in self.env:
        new_targ = ast.Name(id=f"__{node.target.id}", ctx=ast.Load())

        return [
            ast.Assign(
                targets=[new_targ],
                value=self.visit(
                    ast.BinOp(left=node.target, op=node.op, right=node.value)
                ),
            ),
            ast.Assign(
                targets=[node.target],
                value=new_targ,
            ),
        ]

    def visit_For(self, node):
        iter = self.visit(node.iter)

        # Iterate over an object
        if isinstance(iter, ast.Name) and iter.id in self.env:
            if isinstance(self.env[iter.id], ast.Tuple):
                iter = self.env[iter.id].elts

            elif isinstance(self.env[iter.id], ast.Subscript):
                if sys.version_info < (3, 9):
                    _elts = self.env[iter.id].slice.value.elts
                else:
                    _elts = self.env[iter.id].slice.elts

                iter = [
                    ast.Subscript(
                        value=ast.Name(id=iter.id, ctx=ast.Load()),
                        slice=ast.Constant(value=e),
                        ctx=ast.Load(),
                    )
                    for e in range(len(_elts))
                ]
        elif isinstance(iter, ast.Tuple):
            iter = iter.elts

        rolls = []
        for i in iter:
            if isinstance(i, ast.Subscript) or isinstance(i, ast.Constant):
                _val = i
            else:
                _val = ast.Constant(value=i)

            self.const[node.target.id] = _val

            tar_assign = self.visit(ast.Assign(targets=[node.target], value=_val))
            rolls.extend(flatten([tar_assign]))

            new_body = [
                NameValReplacer(node.target.id, _val).visit(copy.deepcopy(b))
                for b in node.body
            ]
            rolls.extend(flatten([self.visit(copy.deepcopy(b)) for b in new_body]))

        return rolls

    def __call_range(self, node):
        if not all([isinstance(a, ast.Constant) for a in node.args]):
            raise Exception("not handled")

        args = [a.value for a in node.args]
        it = list(range(*args))
        return it

    def __call_len(self, node):
        if len(node.args) != 1:
            raise Exception("not handled")

        args = self.__unroll_arg(node.args[0])
        return ast.Constant(value=len(args))

    def __call_minmax(self, node):
        if len(node.args) == 1:
            args = self.__unroll_arg(node.args[0])
        else:
            args = node.args

        op = ast.Gt() if node.func.id == "max" else ast.LtE()

        def iterif(arg_l):
            if len(arg_l) == 1:
                return arg_l[0]
            else:
                comps = [
                    ast.Compare(left=arg_l[0], ops=[op], comparators=[l_it])
                    for l_it in arg_l[1:]
                ]
                comp = ast.BoolOp(op=ast.And(), values=comps)
                return ast.IfExp(test=comp, body=arg_l[0], orelse=iterif(arg_l[1:]))

        return iterif(args)

    def visit_Call(self, node):
        node.args = [self.visit(ar) for ar in node.args]
        if not hasattr(node.func, "id"):
            return node

        if node.func.id == "print":
            return None

        elif node.func.id == "range":
            return self.__call_range(node)

        elif node.func.id == "len":
            return self.__call_len(node)

        elif node.func.id in ["min", "max"]:
            return self.__call_minmax(node)

        else:
            return node


def ast2ast(a_tree):
    # print(ast.dump(a_tree))
    a_tree = ASTRewriter().visit(a_tree)
    # print(ast.dump(a_tree))
    return a_tree
