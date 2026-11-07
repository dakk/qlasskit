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

from typing import Any

from sympy import Symbol
from sympy.logic.boolalg import BooleanFalse, BooleanTrue

from ..qcircuit import QCircuitWrapper
from ..qlassfun import QlassF
from ..types import type_repr


class ConstantOracleException(Exception):
    pass


def oraclize(qf: QlassF, element: Any, name="oracle"):
    """Transform a QlassF qf and an element to an oracle {f(x) = x == element}"""
    argt_name = type_repr(qf.args[0].ttype)

    if qf.name == name:
        qf.name = f"_{name}"

    fs = f"def {name}(v: {argt_name}) -> bool:\n   return {qf.name}(v) == {element}"
    oracle = QlassF.from_function(fs, defs=[qf.to_logicfun()])

    if (
        len(oracle.expressions) == 1
        and oracle.expressions[0][0] == Symbol("_ret")
        and (
            isinstance(oracle.expressions[0][1], BooleanTrue)
            or isinstance(oracle.expressions[0][1], BooleanFalse)
        )
    ):
        raise ConstantOracleException(
            f"The oracle is constant: {oracle.expressions[0][1]}"
        )

    return oracle


class QAlgorithm(QCircuitWrapper):
    def __init__(self):
        pass
