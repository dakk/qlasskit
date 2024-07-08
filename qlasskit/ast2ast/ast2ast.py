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
import sys
from ast import NodeTransformer

from .astrewriter import ASTRewriter
from .constantfolder import ConstantFolder
from .replacemultitargetassign import ReplaceMultiTargetAssign
from .replacetypeann import ReplaceTypeAnn


class IndexReplacer(NodeTransformer):
    """Replace Index with its content (for python < 3.9)"""

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_Index(self, node):
        return self.visit(node.value)


def ast2ast(a_tree):
    # print(ast.dump(a_tree))

    # Replace indexes with its content if python < 3.9
    if sys.version_info < (3, 9):
        a_tree = IndexReplacer().visit(a_tree)

    # Fold constants
    a_tree = ConstantFolder().visit(a_tree)

    # Replace Type Annotations
    a_tree = ReplaceTypeAnn().visit(a_tree)

    # Replace multi-target assign
    a_tree = ReplaceMultiTargetAssign().visit(a_tree)

    # Rewrite the ast
    a_tree = ASTRewriter().visit(a_tree)

    # print(ast.dump(a_tree))
    return a_tree
