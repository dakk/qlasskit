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

from .constantfolder import ConstantFolder
from .replacemultitargetassign import ReplaceMultiTargetAssign
from .replacetypeann import ReplaceTypeAnn


def ast2ast(a_tree: ast.AST) -> ast.AST:
    # print(ast.dump(a_tree))

    # Fold constants
    a_tree = ConstantFolder().visit(a_tree)

    # Replace Type Annotations
    a_tree = ReplaceTypeAnn().visit(a_tree)

    # Replace multi-target assign
    a_tree = ReplaceMultiTargetAssign().visit(a_tree)

    # Fold constants again
    a_tree = ConstantFolder().visit(a_tree)

    # print(ast.dump(a_tree))
    return a_tree
