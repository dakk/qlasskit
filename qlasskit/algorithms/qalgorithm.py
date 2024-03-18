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
