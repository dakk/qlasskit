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
from typing import Optional

from .env import Environment


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
