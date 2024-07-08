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


class ReplaceMultiTargetAssign(ast.NodeTransformer):

    def visit_Assign(self, node):
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
