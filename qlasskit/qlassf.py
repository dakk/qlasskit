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
import inspect
from typing import Callable, List, Tuple, Union  # noqa: F401

from . import ast2logic, compiler
from .typing import *  # noqa: F403, F401
from .typing import Args, BoolExpList

MAX_TRUTH_TABLE_SIZE = 20


class QlassF:
    """Class representing a quantum classical circuit"""

    name: str
    original_f: Callable
    args: Args
    ret_size: int
    expressions: BoolExpList

    def __init__(
        self,
        name: str,
        original_f: Callable,
        args: Args,
        ret_size: int,
        exps: BoolExpList,
    ):
        self.name = name
        self.original_f = original_f
        self.args = args
        self.ret_size = ret_size
        self.expressions = exps

        self._compiled_gate = None

    def __repr__(self):
        arg_str = ", ".join(map(lambda arg: f"{arg[0]}:{arg[1]}", self.args))
        exp_str = "\n\t".join(map(lambda exp: f"{exp[0]} = {exp[1]}", self.expressions))
        return f"QlassF<{self.name}>({arg_str}) -> bool[{self.ret_size}]:\n\t{exp_str}"

    def __add__(self, qf2) -> "QlassF":
        """Adds two qlassf and return the combination"""
        raise Exception("not implemented")

    def truth_table_header(self) -> List[str]:
        """Returns the list of string containing the truth table header"""
        header = [x for x in self.args]
        header.extend([sym.name for (sym, retex) in self.expressions[-self.ret_size :]])
        return header

    def truth_table(self) -> List[List[bool]]:
        """Returns the truth table for the function using the sympy boolean for computing"""
        truth = []
        bits = len(self.args)

        if (bits + self.ret_size) > MAX_TRUTH_TABLE_SIZE:
            raise Exception(
                f"Max truth table size reached: {bits + self.ret_size} > {MAX_TRUTH_TABLE_SIZE}"
            )

        for i in range(2**bits):
            bin_str = bin(i)[2:]
            bin_str = "0" * (bits - len(bin_str)) + bin_str
            bin_arr = list(map(lambda c: c == "1", bin_str))
            known = list(zip(self.args, bin_arr))

            for ename, exp in self.expressions:
                exp_sub = exp.subs(known)
                known.append((ename, exp_sub))

            res = known[0 : len(self.args)] + known[-self.ret_size :]
            res_clean = list(map(lambda y: y[1], res))
            truth.append(res_clean)

        return truth

    def compile(self):
        self._compiled_gate = compiler.to_quantum(
            self.args, self.ret_size, self.expressions
        )

    def gate(self, framework="qiskit"):
        """Returns the gate for a specific framework"""
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")

        if framework == "qiskit":
            g = self._compiled_gate.export(mode="gate", framework=framework)
            g.name = self.name
            return g
        else:
            raise Exception(f"Framework {framework} not supported")

    def qubits(self, index=0):
        """List of qubits of the gate"""
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")
        return self._compiled_gate.qubit_map.values()

    @property
    def res_qubits(self) -> List[int]:
        """Return the qubits holding the result"""
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")
        return [self._compiled_gate.res_qubit]

    @property
    def num_qubits(self) -> int:
        """Return the number of qubits"""
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")
        return self._compiled_gate.num_qubits

    @property
    def input_size(self) -> int:
        """Return the size of the inputs"""
        return len(self.args)

    def bind(self, **kwargs) -> "QlassF":
        """Returns a new QlassF with defined params"""
        raise Exception("not implemented")

    def f(self) -> Callable:
        """Returns the classical python function"""
        return self.original_f

    @staticmethod
    def from_function(f: Union[str, Callable], to_compile=True) -> "QlassF":
        """Create a QlassF from a function or a string containing a function"""
        if isinstance(f, str):
            exec(f)

        fun_ast = ast.parse(f if isinstance(f, str) else inspect.getsource(f))
        fun = fun_ast.body[0]

        fun_name, args, fun_ret, exps = ast2logic.translate_ast(fun)
        original_f = eval(fun_name) if isinstance(f, str) else f

        qf = QlassF(fun_name, original_f, args, fun_ret, exps)
        if to_compile:
            qf.compile()
        return qf


def qlassf(f: Union[str, Callable], to_compile=True) -> QlassF:
    """Decorator / function creating a QlassF object

    Args:
        f: String or function
    """
    return QlassF.from_function(f, to_compile)
