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
from typing import Any, Dict, Union


class Environment:
    types: Dict[str, ast.AST]
    constants: Dict[str, Any]

    def __init__(self):
        self.types = {}
        self.constants = {}

    def set_type(self, name: str, type_annotation: ast.AST) -> None:
        self.types[name] = type_annotation

    def set_constant(self, name: str, value: Union[ast.Constant, Any]) -> None:
        if isinstance(value, ast.Constant):
            return self.set_constant(name, value.value)

        self.constants[name] = value

        if name not in self.types:
            self.types[name] = value

    def copy_type(self, origin: str, dest: str) -> None:
        self.types[dest] = self.types[origin]

    def get_type(self, name: str):  # -> Optional[ast.AST]:
        return self.types.get(name)

    def get_constant(self, name: str):  # -> Optional[Any]:
        return self.constants.get(name)

    def has_type(self, name: str) -> bool:
        return name in self.types

    def has_constant(self, name: str) -> bool:
        return name in self.constants

    def remove(self, name: str) -> None:
        self.types.pop(name, None)
        self.constants.pop(name, None)

    def __contains__(self, name: str):
        return name in self.types or name in self.constants

    def __getitem__(self, name: str) -> Union[Any, ast.AST]:
        if name in self.constants:
            return self.constants[name]
        return self.types.get(name)

    def __setitem__(self, name: str, value: Union[ast.Constant, Any, ast.AST]) -> None:
        if isinstance(value, ast.AST):
            self.set_type(name, value)
        else:
            self.set_constant(name, value)
