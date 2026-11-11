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
