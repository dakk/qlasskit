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
from dataclasses import dataclass
from typing import Any

from ..ast2logic import flatten
from .env import Environment


def create_if_exp(nname, iname, max_i, jname=None, max_j=None):
    """Given a List or List of List `nname`, an index `iname` and an optional index `jname`,
    returns L[0] if i == 0 else L[1] if i == 1 ..."""

    def access_ij(i, j):
        fsub = ast.Subscript(
            value=ast.Name(id=nname, ctx=ast.Load()),
            slice=ast.Constant(value=i),
            ctx=ast.Load(),
        )

        if jname is not None:
            return ast.Subscript(
                value=fsub,
                slice=ast.Constant(value=j),
                ctx=ast.Load(),
            )
        else:
            return fsub

    def _create_if_exp(i, j=None):
        if i == max_i and (jname is None or j == max_j):
            return access_ij(i, j)
        else:
            cmp_i = ast.Compare(
                left=ast.Name(id=iname, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=i)],
            )
            if jname is not None:
                next_j = j + 1 if j < max_j else 0
                next_i = i if j < max_j else i + 1

                return ast.IfExp(
                    test=ast.BoolOp(
                        op=ast.And(),
                        values=[
                            cmp_i,
                            ast.Compare(
                                left=ast.Name(id=jname, ctx=ast.Load()),
                                ops=[ast.Eq()],
                                comparators=[ast.Constant(value=j)],
                            ),
                        ],
                    ),
                    body=access_ij(i, j),
                    orelse=_create_if_exp(next_i, next_j),
                )
            else:
                return ast.IfExp(
                    test=cmp_i,
                    body=access_ij(i, j),
                    orelse=_create_if_exp(i + 1),
                )

    return _create_if_exp(0, None if jname is None else 0)


@dataclass
class IsNamePresent(ast.NodeVisitor):
    """Check if a tree contains a specific name_id"""

    name_id: str
    present: bool = False

    def visit_Name(self, node):
        if node.id == self.name_id:
            self.present = True


@dataclass
class NameValReplacer(ast.NodeTransformer):
    """Replace all Name with name_id with the given val"""

    name_id: str
    val: Any

    def visit_Name(self, node):
        if node.id == self.name_id:
            return self.val

        return node


class ASTRewriter(ast.NodeTransformer):
    """Rewrites the ast to a simplified version"""

    def __init__(self, env=None, ret=None):
        self.env = Environment() if env is None else env
        self.ret = None
        self._uniqd = 1

    @property
    def uniqd(self):
        """Return an unique identifier as str"""
        self._uniqd += 1
        return f"{self._uniqd:x}"

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_Subscript(self, node):  # noqa: C901
        # Replace L[a] with const a, to L[const]
        if isinstance(node.slice, ast.Name) and self.env.has_constant(node.slice.id):
            node.slice = self.env.get_constant(node.slice.id)

        # Handle inner access L[i]
        elif isinstance(node.value, ast.Name) and isinstance(node.slice, ast.Name):
            nname = node.value.id
            iname = node.slice.id

            # Infer i and j sizes from env['a']
            gtype = self.env.get_type(nname)

            if isinstance(gtype, ast.Tuple):
                max_i = len(gtype.elts) - 1
            else:
                outer_tuple = gtype.slice
                max_i = len(outer_tuple.elts) - 1

            # Create the IfExp structure
            return create_if_exp(nname, iname, max_i)

        # Handle inner access L[i][j]
        elif (
            isinstance(node.value, ast.Subscript)
            and isinstance(node.value.value, ast.Name)
            and isinstance(node.value.slice, ast.Name)
            and isinstance(node.slice, ast.Name)
        ):
            nname = node.value.value.id
            iname = node.value.slice.id
            jname = node.slice.id

            # Infer i and j sizes from env['a']
            gtype = self.env.get_type(nname)

            if isinstance(gtype, ast.Tuple) and isinstance(gtype.elts[0], ast.Tuple):
                max_i = len(gtype.elts) - 1
                max_j = len(gtype.elts[0].elts) - 1
            else:
                outer_tuple = gtype.slice
                max_i = len(outer_tuple.elts) - 1
                inner_tuple = outer_tuple.elts
                max_j = len(inner_tuple) - 1

            # Create the IfExp structure
            return create_if_exp(nname, iname, max_i, jname, max_j)

        # Unroll L[a] with (L[0] if a == 0 else L[1] if a == 1 ...) when L is constant
        elif (
            isinstance(node.slice, ast.Name)
            and not self.env.has_constant(node.slice.id)
        ) or isinstance(node.slice, ast.Subscript):
            if isinstance(node.value, ast.Name):
                if node.value.id == "Tuple":
                    return node

                tup = self.env.get_constant(node.value.id)
            else:
                tup = node.value

            if not isinstance(tup, ast.Tuple):
                raise Exception(
                    "Not a tuple in ast2ast visit subscript with not constant node.slice: "
                    + ast.dump(tup)
                )

            elts = tup.elts

            ifex = ast.IfExp(
                test=ast.Compare(
                    left=node.slice, ops=[ast.Eq()], comparators=[ast.Constant(value=0)]
                ),
                body=elts[0],
                orelse=ast.Constant(value=0),
            )
            for i, x in enumerate(elts[1:]):
                ifex = ast.IfExp(
                    test=ast.Compare(
                        left=node.slice,
                        ops=[ast.Eq()],
                        comparators=[ast.Constant(value=i + 1)],
                    ),
                    body=x,
                    orelse=ifex,
                )
            return ifex

        return node

    def visit_Name(self, node):
        # __ prefix is reserved for internal use
        if node.id.startswith("__"):
            raise Exception("invalid name starting with __")

        return node

    def visit_If(self, node):
        """Replace if(c,t,e) with if(c,t1), if(c,t2), ..., if(!c, e1), ..."""
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

            if len(b.targets) != 1 or not isinstance(b.targets[0], ast.Name):
                raise Exception("if targets only allow one Name target: ", ast.dump(b))

            target = b.targets[0].id

            if target.startswith("__") and target not in self.env:
                orelse_inner = ast.Name(id=target[2:])
            else:
                orelse_inner = ast.Name(id=target)

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

            if len(b.targets) != 1 or not isinstance(b.targets[0], ast.Name):
                raise Exception("if targets only allow one Name target: ", ast.dump(b))

            target = b.targets[0].id

            if target.startswith("__") and target not in self.env:
                orelse_inner = ast.Name(id=target[2:])
            elif target[0 : len("_iftarg")] == "_iftarg":
                if_l.append(b)
                continue
            else:
                orelse_inner = ast.Name(id=target)

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
        """Converts List to Tuple"""
        return ast.Tuple(elts=[self.visit(el) for el in node.elts])

    def visit_AnnAssign(self, node):
        node.value = self.visit(node.value) if node.value else node.value
        self.env.set_type(node.target.id, node.annotation)
        return node

    def visit_FunctionDef(self, node):
        for x in node.args.args:
            self.env.set_type(x.arg, x.annotation)

        self.ret = node.returns

        return super().generic_visit(node)

    def visit_Assign(self, node):
        target = node.targets[0].id
        was_known = target in self.env

        if isinstance(node.value, ast.Constant):
            self.env.set_constant(target, node.value)
        elif isinstance(node.value, ast.Name) and node.value.id in self.env:
            self.env.copy_type(node.value.id, target)
        elif isinstance(node.value, ast.Tuple) or isinstance(node.value, ast.List):
            self.env.set_constant(target, self.visit(node.value))
        else:
            self.env.set_type(target, "Unknown")

        # If value is not self referencing, we can skip this (ie: a = b + 1)
        ip = IsNamePresent(target)
        ip.visit(node.value)

        # Reassigning an already present variable (use a temp variable)
        if ip.present and was_known and not isinstance(node.value, ast.Constant):
            new_targ = ast.Name(id=f"__{target}", ctx=ast.Load())

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

    def __unroll_arg(self, arg):
        """Transform a node to a list (when is a Tuple or a subscribable type)"""
        if isinstance(arg, ast.Tuple):
            # If it's a tuple, return elts
            return arg.elts
        elif isinstance(arg, ast.Constant) and isinstance(arg.value, ast.Tuple):
            return arg.value.elts
        elif isinstance(arg, ast.Subscript) and isinstance(arg.value, ast.Name):
            _sval = self.env.get_type(arg.value.id)
            if (
                isinstance(_sval, ast.Subscript)
                and isinstance(_sval.slice, ast.Tuple)
                and isinstance(arg.slice, ast.Constant)
            ):
                return [
                    ast.Subscript(
                        value=ast.Subscript(
                            value=ast.Name(id=arg.value.id, ctx=ast.Load()),
                            slice=ast.Constant(value=arg.slice.value, kind=None),
                        ),
                        slice=ast.Constant(value=i, kind=None),
                    )
                    for i in range(len(_sval.slice.elts))
                ]
        elif isinstance(arg, ast.Name):
            # If it's a name, is in env and is a Tuple, return elements
            if (
                self.env.has_type(arg.id)
                and isinstance(self.env.get_type(arg.id), ast.Subscript)
                and self.env.get_type(arg.id).value.id == "Tuple"
            ):
                _sval = self.env.get_type(arg.id).slice

                return [
                    ast.Subscript(
                        value=ast.Name(id=arg.id, ctx=ast.Load()),
                        slice=ast.Constant(value=i, kind=None),
                    )
                    for i in range(len(_sval.elts))
                ]
            # If it's a tuple constant, return elements
            elif self.env.has_constant(arg.id) and isinstance(
                self.env.get_type(arg.id), ast.Tuple
            ):
                return self.env.get_constant(arg.id).elts
        return [arg]

    def visit_For(self, node):
        """Unroll for loops to single iterations"""
        iter = self.__unroll_arg(self.visit(node.iter))
        rolls = []
        iter = flatten(iter)

        for i in iter:
            if isinstance(i, ast.Constant) or isinstance(i, ast.Subscript):
                _val = i
            else:
                _val = ast.Constant(value=i)
            self.env.set_constant(node.target.id, _val)

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
            raise Exception("Range call on not constant arguments is not handled")

        args = [a.value for a in node.args]
        it = list(range(*args))
        return it

    def __call_len(self, node):
        if len(node.args) != 1:
            raise Exception("Len only receives one argument")

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
        if len(node.args) != 1:
            raise Exception(f"sum() takes at most 1 argument ({len(node.args)} given)")

        args = self.__unroll_arg(node.args[0])

        def iterif(arg_l):
            if len(arg_l) == 1:
                return arg_l[0]
            else:
                return ast.BinOp(left=arg_l[0], op=ast.Add(), right=iterif(arg_l[1:]))

        return iterif(args)

    def __call_anyall(self, node):
        if len(node.args) != 1:
            raise Exception(f"any() takes exactly 1 argument ({len(node.args)} given)")

        args = self.__unroll_arg(node.args[0])
        op = ast.Or() if node.func.id == "any" else ast.And()
        return ast.BoolOp(op=op, values=args)

    def __call_chr(self, node):
        if len(node.args) != 1:
            raise Exception(f"chr() takes exactly 1 argument ({len(node.args)} given)")
        return node.args[0]

    def __call_ord(self, node):
        if len(node.args) != 1:
            raise Exception(f"ord() takes exactly 1 argument ({len(node.args)} given)")
        return node.args[0]

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

        elif node.func.id == "ord":
            return self.__call_ord(node)

        elif node.func.id == "chr":
            return self.__call_chr(node)

        elif node.func.id in ["any", "all"]:
            return self.__call_anyall(node)

        elif node.func.id in ["min", "max"]:
            return self.__call_minmax(node)

        else:
            return node

    def visit_BinOp(self, node):
        # Rewrite the ** operator to be a series of multiplications
        if isinstance(node.op, ast.Pow):
            if (
                isinstance(node.right, ast.Constant)
                and isinstance(node.right.value, int)
                and node.right.value > 0
            ):
                result = node.left
                for _ in range(node.right.value - 1):
                    result = ast.BinOp(left=result, op=ast.Mult(), right=node.left)
                return result

            elif (
                isinstance(node.right, ast.Constant)
                and isinstance(node.right.value, int)
                and node.right.value == 0
            ):
                return ast.Constant(value=1)

        return super().generic_visit(node)
