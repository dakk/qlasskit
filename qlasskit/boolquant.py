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

from sympy import Function
from sympy.logic.boolalg import Boolean


class QuantumBooleanGate(Function, Boolean):
    # TODO: add an eval method to be able to simplify H(H(a)) => a

    def build(name: str):
        return type(name, (QuantumBooleanGate,), {})


class Q:
    """An identity wrapper for python"""

    def H(*args):
        return args

    def Z(*args):
        return args

    def Y(*args):
        return args

    def X(*args):
        return args

    def T(*args):
        return args

    def S(*args):
        return args

    def CX(*args):
        return args

    def MCX(*args):
        return args
