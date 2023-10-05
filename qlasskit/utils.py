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
from sympy.logic.boolalg import And, BooleanFunction, Xor


class BToffoli(BooleanFunction):
    """
    Logical Toffoli function; invert the third argument, if the first two are True.

    c XOR (a AND b)

    Examples
    ========

    >>> BToffoli(False, False, True)
    True
    >>> BToffoli(True, True, True)
    False
    >>> BToffoli(True, True, False)
    True

    """

    @classmethod
    def eval(cls, a, b, c):
        return Xor(c, And(a, b))
