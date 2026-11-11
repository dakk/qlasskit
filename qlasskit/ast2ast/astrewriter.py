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
from dataclasses import dataclass
from typing import Optional, Union

from .constantfolder import ConstantFolder
from .env import Environment


@dataclass
class IsNamePresent(ast.NodeVisitor):
    """Check if a tree contains a specific name_id"""

    name_id: str
    present: bool = False

    def visit_Name(self, node: ast.Name):
        if node.id == self.name_id:
            self.present = True


class ASTRewriter(ast.NodeTransformer):
    """Rewrites the ast to a simplified version"""

    env: Environment

    def __init__(self, env: Optional[Environment] = None, ret=None):
        self.env = Environment() if env is None else env
        self.ret = None
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

    def visit_Name(self, node: ast.Name):
        # __ prefix is reserved for internal use
        if node.id.startswith("__"):
            raise Exception("invalid name starting with __")

        return node

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
