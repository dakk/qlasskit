# Copyright 2023-2025 Davide Gessa

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
