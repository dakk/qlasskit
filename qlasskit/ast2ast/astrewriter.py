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
from dataclasses import dataclass
from typing import Any, Optional, Union

from ..ast2logic import flatten
from .constantfolder import ConstantFolder
from .env import Environment


def iterator_accessor(
    n_name: str, i_name: str, i_max: int
) -> Union[ast.Subscript, ast.IfExp]:
    """Given a List `n_name`, an index `i_name` returns L[0] if i == 0 else L[1] if i == 1 ..."""
    res: Union[ast.Subscript, ast.IfExp] = ast.Subscript(
        value=ast.Name(id=n_name, ctx=ast.Load()),
        slice=ast.Constant(value=0),
        ctx=ast.Load(),
    )
    for i in range(1, i_max + 1):
        cmp_i = ast.Compare(
            left=ast.Name(id=i_name, ctx=ast.Load()),
            ops=[ast.Eq()],
            comparators=[ast.Constant(value=i)],
        )
        res = ast.IfExp(
            test=cmp_i,
            body=ast.Subscript(
                value=ast.Name(id=n_name, ctx=ast.Load()),
                slice=ast.Constant(value=i),
                ctx=ast.Load(),
            ),
            orelse=res,
        )

    return res


def iterator_accessor2(
    n_name: str,
    i_name: str,
    i_max: int,
    j_name: str,
    j_max: int,
) -> Union[ast.Subscript, ast.IfExp]:
    """Given a List of List `n_name`, an index `i_name` and an optional index `j_name`,
    returns L[0][0] if i == 0 and j == 0 else L[0][1] if i == 0 and j == 1 ..."""

    def access_ij(i: int, j: int) -> ast.Subscript:
        "Return [i][j] subscript of name"
        return ast.Subscript(
            value=ast.Subscript(
                value=ast.Name(id=n_name, ctx=ast.Load()),
                slice=ast.Constant(value=i),
                ctx=ast.Load(),
            ),
            slice=ast.Constant(value=j),
            ctx=ast.Load(),
        )

    res: Union[ast.Subscript, ast.IfExp] = access_ij(0, 0)

    for i in range(i_max + 1):
        for j in range(j_max + 1):
            if i == 0 and j == 0:
                continue

            cmp_i = ast.Compare(
                left=ast.Name(id=i_name, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=i)],
            )

            cmp_j = ast.Compare(
                left=ast.Name(id=j_name, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=j)],
            )

            res = ast.IfExp(
                test=ast.BoolOp(
                    op=ast.And(),
                    values=[cmp_i, cmp_j],
                ),
                body=access_ij(i, j),
                orelse=res,
            )

    return res


@dataclass
class IsNamePresent(ast.NodeVisitor):
    """Check if a tree contains a specific name_id"""

    name_id: str
    present: bool = False

    def visit_Name(self, node: ast.Name):
        if node.id == self.name_id:
            self.present = True


@dataclass
class NameValReplacer(ast.NodeTransformer):
    """Replace all Name with name_id with the given val"""

    name_id: str
    val: Any

    def visit_Name(self, node: ast.Name):
        if node.id == self.name_id:
            return self.val

        return node


class ASTRewriter(ast.NodeTransformer):
    """Rewrites the ast to a simplified version"""

    env: Environment

    def __init__(self, env: Optional[Environment] = None, ret=None):
        self.env = Environment() if env is None else env
        self.ret = None
        self._uniqd = 1
        self.__call_dispatch = {
            "range": self.__call_range,
            "len": self.__call_len,
            "sum": self.__call_sum,
            "ord": self.__call_ord,
            "chr": self.__call_chr,
            "any": self.__call_anyall,
            "all": self.__call_anyall,
            "min": self.__call_minmax,
            "max": self.__call_minmax,
        }

    @property
    def uniqd(self):
        """Return an unique identifier as str"""
        self._uniqd += 1
        return f"{self._uniqd:x}"

    def visit_Subscript(self, node: ast.Subscript):  # noqa: C901
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
            return iterator_accessor(nname, iname, max_i)

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
            return iterator_accessor2(nname, iname, max_i, jname, max_j)

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

            if isinstance(tup, ast.Constant):
                tup = tup.value

            if not isinstance(tup, ast.Tuple):
                raise Exception(
                    "Not a tuple in ast2ast visit subscript with not constant node.slice: "
                    + ast.dump(tup)
                )

            elts = tup.elts

            ifex = elts[0]

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

    def visit_Name(self, node: ast.Name):
        # __ prefix is reserved for internal use
        if node.id.startswith("__"):
            raise Exception("invalid name starting with __")

        return node

    def visit_If(self, node: ast.If):
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

    def visit_List(self, node: ast.List):
        """Converts List to Tuple"""
        return ast.Tuple(elts=[self.visit(el) for el in node.elts])

    def visit_AnnAssign(self, node: ast.AnnAssign):
        node.value = self.visit(node.value) if node.value else node.value

        if hasattr(node.target, "id"):
            self.env.set_type(node.target.id, node.annotation)

        return node

    def visit_FunctionDef(self, node):
        for x in node.args.args:
            self.env.set_type(x.arg, x.annotation)

        self.ret = node.returns

        return super().generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        if not hasattr(node.targets[0], "id"):
            raise ValueError(node.targets[0], "has no id")

        target = node.targets[0].id
        was_known = target in self.env

        if isinstance(node.value, ast.Constant):
            self.env.set_constant(target, node.value)
        elif isinstance(node.value, ast.Name) and node.value.id in self.env:
            self.env.copy_type(node.value.id, target)
        elif isinstance(node.value, ast.Tuple) or isinstance(node.value, ast.List):
            self.env.set_constant(target, self.visit(node.value))
        else:
            self.env.set_type(target, "Unknown")  # type: ignore

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

    def __unroll_arg(
        self, arg: Union[ast.Constant, ast.Subscript, ast.Tuple, ast.Name]
    ):
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

    def visit_For(self, node: ast.For):
        """Unroll for loops to single iterations"""
        if not hasattr(node.target, "id"):
            raise ValueError(node.target, "has no id")

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
        node = ConstantFolder().visit(node)

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
                comp = ast.BoolOp(op=ast.And(), values=comps)  # type: ignore
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

    def visit_Call(self, node: ast.Call):
        node.args = [self.visit(ar) for ar in node.args]
        if not hasattr(node.func, "id"):
            return node

        handler = self.__call_dispatch.get(node.func.id)
        return handler(node) if handler is not None else node
