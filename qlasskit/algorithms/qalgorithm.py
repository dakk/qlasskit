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

import sys
from typing import Any, Dict, List, Optional, Union, get_args

from sympy import Symbol
from sympy.logic.boolalg import BooleanFalse, BooleanTrue

from ..qcircuit import QCircuit, SupportedFramework
from ..qlassf import QlassF


def format_outcome(
    out: Union[str, int, List[bool]], out_len: Optional[int] = None
) -> List[bool]:
    if isinstance(out, str):
        return format_outcome([True if c == "1" else False for c in out], out_len)
    elif isinstance(out, int):
        return format_outcome(str(bin(out))[2:], out_len)
    elif isinstance(out, List):
        if out_len is None:
            out_len = len(out)

        if len(out) < out_len:
            out += [False] * (out_len - len(out))

        return out
    raise Exception(f"Invalid format: {out}")


def interpret_as_qtype(
    out: Union[str, int, List[bool]], qtype, out_len: Optional[int] = None
) -> Any:
    out = list(reversed(format_outcome(out, out_len)))

    def _interpret(out, qtype, out_len):
        if hasattr(qtype, "from_bool"):
            return qtype.from_bool(out[0:out_len])  # type: ignore
        elif qtype == bool:
            return out[0]
        else:  # Tuple
            idx_s = 0
            values = []
            for x in get_args(qtype):
                len_a = x.BIT_SIZE if hasattr(x, "BIT_SIZE") else 1
                values.append(_interpret(out[idx_s : idx_s + len_a], x, len_a))
                idx_s += len_a

            return tuple(values)

    return _interpret(out, qtype, out_len)


class ConstantOracleException(Exception):
    pass


def oraclize(qf: QlassF, element: Any, name="oracle"):
    """Transform a QlassF qf and an element to an oracle {f(x) = x == element}"""
    if hasattr(qf.args[0].ttype, "__name__"):
        argt_name = qf.args[0].ttype.__name__  # type: ignore

        args = get_args(qf.args[0].ttype)
        if len(args) > 0:
            argt_name += "["
            argt_name += ",".join([x.__name__ for x in args])
            argt_name += "]"

    elif qf.args[0].ttype == bool:
        argt_name = "bool"
    elif sys.version_info < (3, 9):
        argt_name = "Tuple["
        argt_name += ",".join([x.__name__ for x in get_args(qf.args[0].ttype)])
        argt_name += "]"

    if qf.name == name:
        qf.name = f"_{name}"

    oracle = QlassF.from_function(
        f"def {name}(v: {argt_name}) -> bool:\n   return {qf.name}(v) == {element}",
        defs=[qf.to_logicfun()],
    )

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


class QAlgorithm:
    qc: QCircuit

    def __init__(self):
        pass

    def interpret_outcome(self, outcome: Union[str, int, List[bool]]) -> Any:
        """Get the quantum circuit outcome, and return a meaningful data

        Args:
            outcome: the binary string / number to interpret

        Returns:
            Any: the outcome in a meaningful format
        """
        raise Exception("abstract")

    def out_qubits(self) -> List[int]:
        """Returns a list of output qubits"""
        raise Exception("abstract")

    def interpet_counts(self, counts: Dict[str, int]) -> Dict[Any, int]:
        """Interpet data inside a circuit counts dict"""
        outcomes = [(self.interpret_outcome(e), c) for (e, c) in counts.items()]
        int_counts: Dict[Any, int] = {}
        for e, c in outcomes:
            if e in int_counts:
                int_counts[e] += c
            else:
                int_counts[e] = c
        return int_counts

    def export(self, framework: SupportedFramework = "qiskit") -> Any:
        """Export the algorithm to a supported framework"""
        return self.qc.export(mode="circuit", framework=framework)
