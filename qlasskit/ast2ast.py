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


class IndexReplacer(ast.NodeTransformer):
    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_Index(self, node):
        return self.visit(node.value)


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


def _replace_types_annotations(ann, arg=None):
    if isinstance(ann, ast.Subscript) and ann.value.id == "Tuple":
        _elts = ann.slice.elts
        _ituple = ast.Tuple(elts=[_replace_types_annotations(el) for el in _elts])

        ann = ast.Subscript(
            value=ast.Name(id="Tuple", ctx=ast.Load()),
            slice=_ituple,
        )

    # Replace Qlist[T,n] with Tuple[(T,)*n]
    if isinstance(ann, ast.Subscript) and ann.value.id == "Qlist":
        _elts = ann.slice.elts
        _ituple = ast.Tuple(elts=[copy.deepcopy(_elts[0])] * _elts[1].value)

        ann = ast.Subscript(
            value=ast.Name(id="Tuple", ctx=ast.Load()),
            slice=_ituple,
        )

    # Replace Qmatrix[T,n,m] with Tuple[(Tuple[(T,)*m],)*n]
    if isinstance(ann, ast.Subscript) and ann.value.id == "Qmatrix":
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


class ASTRewriter(ast.NodeTransformer):
    """Rewrites the ast to a simplified version"""

    def __init__(self, env={}, ret=None):
        self.env = {}
        self.const = {}
        self.ret = None
        self._uniqd = 1

    @property
    def uniqd(self):
        """Return an unique identifier as str"""
        self._uniqd += 1
        return f"{hex(self._uniqd)[2:]}"

    def __unroll_arg(self, arg):
        if isinstance(arg, ast.Tuple):
            return arg.elts
        elif isinstance(arg, ast.Name):
            if (
                arg.id in self.env
                and isinstance(self.env[arg.id], ast.Subscript)
                and self.env[arg.id].value.id == "Tuple"
            ):
                _sval = self.env[arg.id].slice

                return [
                    ast.Subscript(
                        value=ast.Name(id=arg.id, ctx=ast.Load()),
                        slice=ast.Constant(value=i, kind=None),
                    )
                    for i in range(len(_sval.elts))
                ]
        return [arg]

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_Subscript(self, node):
        _sval = node.slice

        if isinstance(_sval, ast.Name) and _sval.id in self.const:
            node.slice = self.const[_sval.id]

        # Unroll L[a] with (L[0] if a == 0 else L[1] if a == 1 ...)
        elif (isinstance(_sval, ast.Name) and _sval.id not in self.const) or isinstance(
            _sval, ast.Subscript
        ):
            if isinstance(node.value, ast.Name):
                if node.value.id == "Tuple":
                    return node

                tup = self.env[node.value.id]
            else:
                tup = node.value

            if not isinstance(tup, ast.Tuple):
                raise Exception(
                    "Not a tuple in ast2ast visit subscript with not constant _sval"
                )

            elts = tup.elts

            ifex = ast.IfExp(
                test=ast.Compare(
                    left=_sval, ops=[ast.Eq()], comparators=[ast.Constant(value=0)]
                ),
                body=elts[0],
                orelse=ast.Constant(value=0),
            )
            for i, x in enumerate(elts[1:]):
                ifex = ast.IfExp(
                    test=ast.Compare(
                        left=_sval,
                        ops=[ast.Eq()],
                        comparators=[ast.Constant(value=i + 1)],
                    ),
                    body=x,
                    orelse=ifex,
                )
            return ifex

        return node

    def visit_Name(self, node):
        if node.id[0:2] == "__":
            raise Exception("invalid name starting with __")

        return node

    def visit_If(self, node):
        body = flatten([self.visit(n) for n in node.body])
        orelse = flatten([self.visit(n) for n in node.orelse])
        test_name = "_iftarg" + self.uniqd

        if_l = [
            ast.Assign(
                targets=[ast.Name(id=test_name)],
                value=self.visit(node.test),
            )
        ]

        for b in body:
            if not isinstance(b, ast.Assign):
                raise Exception("if body only allows assigns: ", ast.dump(b))

            if len(b.targets) != 1:
                raise Exception("if targets only allow one: ", ast.dump(b))

            target_0id = b.targets[0].id

            if target_0id[0:2] == "__" and target_0id not in self.env:
                orelse_inner = ast.Name(id=target_0id[2:])
            else:
                orelse_inner = ast.Name(id=target_0id)

            if_l.append(
                ast.Assign(
                    targets=b.targets,
                    value=ast.IfExp(
                        test=ast.Name(id=test_name), body=b.value, orelse=orelse_inner
                    ),
                )
            )

        for b in orelse:
            if not isinstance(b, ast.Assign):
                raise Exception("if body only allows assigns: ", ast.dump(b))

            if len(b.targets) != 1:
                raise Exception("if targets only allow one: ", ast.dump(b))

            target_0id = b.targets[0].id

            if target_0id[0:2] == "__" and target_0id not in self.env:
                orelse_inner = ast.Name(id=target_0id[2:])
            else:
                orelse_inner = ast.Name(id=target_0id)

            if_l.append(
                ast.Assign(
                    targets=b.targets,
                    value=ast.IfExp(
                        test=ast.Name(id=test_name), orelse=b.value, body=orelse_inner
                    ),
                )
            )

        return if_l

    def visit_List(self, node):
        return ast.Tuple(elts=[self.visit(el) for el in node.elts])

    def visit_AnnAssign(self, node):
        node.annotation = _replace_types_annotations(node.annotation)
        node.value = self.visit(node.value) if node.value else node.value
        self.env[node.target] = node.annotation
        return node

    def visit_FunctionDef(self, node):
        node.args.args = [
            _replace_types_annotations(x.annotation, arg=x) for x in node.args.args
        ]

        for x in node.args.args:
            self.env[x.arg] = x.annotation

        node.returns = _replace_types_annotations(node.returns)
        self.ret = node.returns

        return super().generic_visit(node)

    def visit_Assign(self, node):
        # Transform multi-target assign to single target assigns
        if len(node.targets) == 1 and hasattr(node.targets[0], "elts"):
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

        target_0id = node.targets[0].id
        was_known = target_0id in self.env

        if isinstance(node.value, ast.Name) and node.value.id in self.env:
            self.env[target_0id] = self.env[node.value.id]
        elif isinstance(node.value, ast.Tuple) or isinstance(node.value, ast.List):
            self.env[target_0id] = self.visit(node.value)
        else:
            self.env[target_0id] = "Unknown"

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

    def visit_For(self, node):  # noqa: C901
        iter = self.visit(node.iter)

        # Iterate over an object
        if isinstance(iter, ast.Name) and iter.id in self.env:
            if isinstance(self.env[iter.id], ast.Tuple):
                iter = self.env[iter.id].elts

            elif isinstance(self.env[iter.id], ast.Subscript):
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
        elif isinstance(iter, ast.Subscript) and iter.value.id in self.env:
            if isinstance(self.env[iter.value.id], ast.Tuple):
                iter = self.env[iter.value.id].elts[iter.slice.value]

            elif isinstance(self.env[iter.value.id], ast.Subscript):
                _elts = self.env[iter.value.id].slice.elts[iter.slice.value]

                if isinstance(_elts, ast.Tuple):
                    _elts = _elts.elts

                iter = [
                    ast.Subscript(
                        value=ast.Subscript(
                            value=ast.Name(id=iter.value.id, ctx=ast.Load()),
                            slice=ast.Constant(value=iter.slice.value),
                            ctx=ast.Load(),
                        ),
                        slice=ast.Constant(value=e),
                    )
                    for e in range(len(_elts))
                ]

        if isinstance(iter, ast.Constant) and isinstance(iter.value, ast.Tuple):
            iter = iter.value.elts

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

    def __call_sum(self, node):
        if len(node.args) == 1:
            args = self.__unroll_arg(node.args[0])
        else:
            raise Exception(f"sum() takes at most 1 argument ({len(node.args)} given)")

        def iterif(arg_l):
            if len(arg_l) == 1:
                return arg_l[0]
            else:
                return ast.BinOp(left=arg_l[0], op=ast.Add(), right=iterif(arg_l[1:]))

        return iterif(args)

    def __call_anyall(self, node):
        if len(node.args) == 1:
            args = self.__unroll_arg(node.args[0])
        else:
            raise Exception(f"any() takes exactly 1 argument ({len(node.args)} given)")

        op = ast.Or() if node.func.id == "any" else ast.And()
        return ast.BoolOp(op=op, values=args)

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

        elif node.func.id == "sum":
            return self.__call_sum(node)

        elif node.func.id in ["any", "all"]:
            return self.__call_anyall(node)

        elif node.func.id in ["min", "max"]:
            return self.__call_minmax(node)

        else:
            return node


def ast2ast(a_tree):
    # print(ast.dump(a_tree))
    if sys.version_info < (3, 9):
        a_tree = IndexReplacer().visit(a_tree)

    a_tree = ASTRewriter().visit(a_tree)
    # print(ast.dump(a_tree))
    return a_tree
