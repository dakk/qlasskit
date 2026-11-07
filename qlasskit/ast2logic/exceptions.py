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


class OperationNotSupportedException(Exception):
    def __init__(self, tt, op):
        super().__init__(f"Operation '{op}' not supported by type {tt}")


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


class UnknownSymbolException(Exception):
    def __init__(self, symbol, env):
        super().__init__(f"{symbol} in {env}")
