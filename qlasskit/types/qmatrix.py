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

from typing import Tuple, TypeVar

T = TypeVar("T")


class QmatrixMeta(type):
    def __getitem__(cls, params):
        if isinstance(params, tuple) and len(params) == 3:
            T, n, m = params
            if (
                isinstance(T, type)
                and isinstance(n, int)
                and n > 0
                and isinstance(m, int)
                and m > 0
            ):
                return Tuple[(Tuple[(T,) * n],) * m]


class Qmatrix(metaclass=QmatrixMeta):
    pass


# a: Qmatrix[int, 2, 2] => Tuple[Tuple[int, int], Tuple[int, int]]
