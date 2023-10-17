# Copyright 2023 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Tuple

from typing_extensions import TypeAlias

from ..types import BUILTIN_TYPES, Qint, Qtype  # noqa: F401, E402
from . import exceptions
from .typing import Arg

Binding: TypeAlias = Arg
TypeBinding = Tuple[str, Qtype]


class Env:
    def __init__(self):
        self.bindings: List[Binding] = []
        self.types: List[TypeBinding] = []

        for t in BUILTIN_TYPES:
            self.bind_type((t.__name__, t))

    def bind_type(self, bb: TypeBinding):
        if self.know_type(bb[0]):
            return
        self.types.append(bb)

    def know_type(self, type_name: str) -> bool:
        return len(list(filter(lambda x: x[0] == type_name, self.types))) == 1

    def gettype(self, type_name: str) -> Qtype:
        try:
            return list(filter(lambda x: x[0] == type_name, self.types))[0][1]
        except:
            raise exceptions.UnboundException(type_name, self)

    def bind(self, bb: Binding):
        if bb.name in self:
            raise Exception("duplicate bind")

        self.bindings.append(bb)

    def __contains__(self, key):
        return len(list(filter(lambda x: x.name == key, self.bindings))) == 1

    def __getitem__(self, key):
        try:
            return list(filter(lambda x: x.name == key, self.bindings))[0]
        except:
            raise exceptions.UnboundException(key, self)
