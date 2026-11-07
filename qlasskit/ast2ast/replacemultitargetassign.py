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


class ReplaceMultiTargetAssign(ast.NodeTransformer):
    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) != 1 or not hasattr(node.targets[0], "elts"):
            return node

        # Transform multi-target assign to single target assigns
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
