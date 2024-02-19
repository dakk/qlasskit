# Copyright 2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .qint import Qint7
from .qtype import TExp


class Qchar(Qint7):
    BIT_SIZE = 7

    def __init__(self, value):
        super().__init__()
        self.value = ord(value) % 2**self.BIT_SIZE

    @classmethod
    def comparable(cls, other_type=None) -> bool:
        """Return true if the type is comparable with itself or
        with [other_type]"""
        if not other_type or issubclass(other_type, Qchar):
            return True
        return False

    @classmethod
    def const(cls, v: str) -> TExp:
        """Return the list of bool representing a char"""
        assert len(v) == 1
        cval = list(map(lambda c: True if c == "1" else False, bin(ord(v[0]))[2:]))[
            ::-1
        ]
        return cls.fill((cls, cval))
