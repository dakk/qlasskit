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

from . import ast_to_logic, compiler
from .typing import *  # noqa: F403, F401
from .typing import BoolExpList


class QlassF:
    """Class representing a quantum classical circuit"""

    def __init__(self, name, original_f, args, ret_type, exps):
        self.name = name
        self.original_f = original_f
        self.args = args
        self.ret_type = ret_type
        self.expressions: BoolExpList = exps

        self._compiled_gate = None

    def __repr__(self):
        arg_str = ", ".join(map(lambda arg: f"{arg[0]}:{arg[1]}", self.args))
        exp_str = "\n\t".join(map(lambda exp: f"{exp[0]} = {exp[1]}", self.expressions))
        return f"QlassF<{self.name}>({arg_str}) -> {self.ret_type}:\n\t{exp_str}"

    def __add__(self, qf2) -> "QlassF":
        """Adds two qlassf and return the combination"""
        raise Exception("not implemented")

    def compile(self):
        # TODO: compile all expression and create a one gate only
        self._compiled_gate = compiler.to_quantum(self.expressions)

    def gate(self, framework="qiskit"):
        """Returns the gate for a specific framework"""
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")

        if framework == "qiskit":
            g = self._compiled_gate.to_qiskit()
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
        return len(self.qubits())

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

        fun_name, args, fun_ret, exps = ast_to_logic.translate_ast(fun)
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
