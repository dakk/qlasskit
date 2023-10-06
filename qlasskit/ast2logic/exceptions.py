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

import ast


class TypeErrorException(Exception):
    def __init__(self, got, excepted):
        super().__init__(f"Got '{got}' excepted '{excepted}'")


class NoReturnTypeException(Exception):
    def __init__(self):
        super().__init__("Return type is mandatory")


class StatementNotHandledException(Exception):
    def __init__(self, ob, message=None):
        super().__init__(ast.dump(ob) + f": {message}" if message else "")


class ExpressionNotHandledException(Exception):
    def __init__(self, ob, message=None):
        super().__init__(ast.dump(ob) + f": {message}" if message else "")


class UnknownTypeException(Exception):
    def __init__(self, ob, message=None):
        super().__init__(ast.dump(ob) + f": {message}" if message else "")


class OutOfBoundException(Exception):
    def __init__(self, size, i):
        super().__init__(f"size is {size}: {i} accessed")
        
class UnboundException(Exception):
    def __init__(self, symbol, env):
        super().__init__(f"{symbol} in {env}")


class ConstantReturnException(Exception):
    def __init__(self, name, val):
        super().__init__(f"{name} is costant = {val}")


class SymbolReassignedException(Exception):
    def __init__(self, name):
        super().__init__(f"{name} cannot be reassinged")
