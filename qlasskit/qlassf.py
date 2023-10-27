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
import copy
import inspect
from functools import reduce
from typing import Callable, Dict, List, Tuple, Union  # noqa: F401

from sympy import Symbol
from sympy.logic.boolalg import Boolean

from . import compiler
from .ast2ast import ast2ast
from .ast2logic import Arg, Args, BoolExpList, LogicFun, flatten, translate_ast
from .types import *  # noqa: F403, F401
from .types import Qtype

MAX_TRUTH_TABLE_SIZE = 20


# Remove const exps
def remove_const_exps(exps: BoolExpList, fun_ret: Arg) -> BoolExpList:
    const: Dict[Symbol, Boolean] = {}
    n_exps: BoolExpList = []
    for i in range(len(exps)):
        (s, e) = exps[i]
        e = e.subs(const)
        if (e == False or e == True) and i < (len(exps) - len(fun_ret)):  # noqa: E712
            const[s] = e
        else:
            if s in const:
                del const[s]
            n_exps.append((s, e))

    return n_exps


# Subsitute exps (replace a = ~a, a = ~a, a = ~a => a = ~a)
# def subsitute_exps(exps: BoolExpList, fun_ret: Arg) -> BoolExpList:
#     const: Dict[Symbol, Boolean] = {}
#     n_exps: BoolExpList = []
#     print(exps)

#     for i in range(len(exps)):
#         (s, e) = exps[i]
#         e = e.subs(const)
#         const[s] = e

#         for x in e.free_symbols:
#             if x in const:
#                 n_exps.append((x, const[x]))
#                 del const[x]

#     for (s,e) in const.items():
#         if s == e:
#             continue

#         n_exps.append((s,e))

#     print(n_exps)
#     print()
#     print()
#     return n_exps


# Remove exp like: __a.0 = a.0, ..., a.0 = __a.0
def remove_unnecessary_assigns(exps: BoolExpList) -> BoolExpList:
    n_exps: BoolExpList = []

    def should_add(s, e, n_exps2):
        ename = f"__{s.name}"
        if e.name == ename:
            for s1, e1 in n_exps2[::-1]:
                if s1.name == ename:
                    if isinstance(e1, Symbol) and e1.name == s.name:
                        n_exps2.remove((s1, e1))
                        return False
                    else:
                        return True
        return True

    for s, e in exps:
        if not isinstance(e, Symbol) or should_add(s, e, n_exps):
            n_exps.append((s, e))

    return n_exps


# Translate exp like: __a.0 = !a, a = __a.0 ===> a = !a
def merge_unnecessary_assigns(exps: BoolExpList) -> BoolExpList:
    n_exps: BoolExpList = []

    for s, e in exps:
        if len(n_exps) >= 1 and n_exps[-1][0] == e:
            old = n_exps.pop()
            n_exps.append((s, old[1]))
        else:
            n_exps.append((s, e))

    return n_exps


class QlassF:
    """Class representing a quantum classical circuit"""

    name: str
    original_f: Callable
    args: Args
    returns: Arg
    expressions: BoolExpList

    def __init__(
        self,
        name: str,
        original_f: Callable,
        args: Args,
        returns: Arg,
        exps: BoolExpList,
    ):
        self.name = name
        self.original_f = original_f
        self.args = args
        self.returns = returns
        self.expressions = exps

        self._compiled_gate = None

    def __repr__(self):
        ret_str = f"{self.returns.ttype.__name__}"
        arg_str = ", ".join(
            map(lambda arg: f"{arg.name}:{arg.ttype.__name__}", self.args)
        )
        exp_str = "\n\t".join(map(lambda exp: f"{exp[0]} = {exp[1]}", self.expressions))
        return f"QlassF<{self.name}>({arg_str}) -> {ret_str}:\n\t{exp_str}"

    @property
    def ret_size(self):
        return len(self.returns)

    def __add__(self, qf2) -> "QlassF":
        """Adds two qlassf and return the combination f + g = f(g())"""
        raise Exception("not implemented")

    def truth_table_header(self) -> List[str]:
        """Returns the list of string containing the truth table header"""
        header = flatten(list(map(lambda a: a.bitvec, self.args)))
        header.extend([sym.name for (sym, retex) in self.expressions[-self.ret_size :]])
        return header

    def truth_table(self, max=None) -> List[List[bool]]:
        """Returns the truth table for the function using the sympy boolean for computing

        Args:
            max (int, optional): if set, return max lines, randomly selected
        """
        truth = []
        arg_bits = flatten(list(map(lambda a: a.bitvec, self.args)))
        bits = len(arg_bits)

        if not max and (bits + self.ret_size) > MAX_TRUTH_TABLE_SIZE:
            raise Exception(
                f"Max truth table size reached: {bits + self.ret_size} > {MAX_TRUTH_TABLE_SIZE}"
            )

        for i in range(
            0, 2**bits, int(2**bits / max) if max and max < 2**bits else 1
        ):
            bin_str = bin(i)[2:]
            bin_str = "0" * (bits - len(bin_str)) + bin_str
            bin_arr = list(map(lambda c: c == "1", bin_str))
            known = list(zip(arg_bits, bin_arr))

            for ename, exp in self.expressions:
                exp_sub = exp.subs(known)

                known = list(filter(lambda x: x[0] != ename.name, known))
                known.append(
                    (ename.name if isinstance(ename, Symbol) else ename, exp_sub)
                )

            res = list(zip(arg_bits, bin_arr)) + known[-self.ret_size :]
            res_clean = list(map(lambda y: y[1], res))
            truth.append(res_clean)

        return truth

    def compile(self):
        self._compiled_gate = compiler.to_quantum(
            name=self.name,
            args=self.args,
            returns=self.returns,
            exprs=self.expressions,
        )

    def circuit(self):
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")
        return self._compiled_gate

    def gate(self, framework="qiskit"):
        """Returns the gate for a specific framework"""
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")

        return self._compiled_gate.export(mode="gate", framework=framework)

    # def qubits(self, index=0):
    #     """List of qubits of the gate"""
    #     if self._compiled_gate is None:
    #         raise Exception("Not yet compiled")
    #     return self._compiled_gate.qubit_map.values()

    # @property
    # def res_qubits(self) -> List[int]:
    #     """Return the qubits holding the result"""
    #     if self._compiled_gate is None:
    #         raise Exception("Not yet compiled")
    #     return [self._compiled_gate.res_qubit]

    @property
    def input_size(self) -> int:
        """Return the size of the inputs (in bits)"""
        return reduce(lambda a, b: a + len(b), self.args, 0)

    @property
    def num_qubits(self) -> int:
        """Return the number of qubits"""
        if self._compiled_gate is None:
            raise Exception("Not yet compiled")
        return self._compiled_gate.num_qubits

    def bind(self, **kwargs) -> "QlassF":
        """Returns a new QlassF with defined params"""
        raise Exception("not implemented")

    def f(self) -> Callable:
        """Returns the classical python function"""
        return self.original_f

    def to_logicfun(self) -> LogicFun:
        return copy.deepcopy((self.name, self.args, self.returns, self.expressions))

    @staticmethod
    def from_function(
        f: Union[str, Callable],
        types: List[Qtype] = [],
        defs: List[LogicFun] = [],
        to_compile: bool = True,
    ) -> "QlassF":
        """Create a QlassF from a function or a string containing a function

        Args:
            f (Union[str, Callable]): the function to be parsed, as a str code or callable
            types (List[Qtype]): list of qtypes to inject
            to_compile (boolean, optional): if True, compile to quantum circuit (default: True)
            defs (List[LogicFun]): list of LogicFun to inject
        """
        if isinstance(f, str):
            exec(f)

        fun_ast = ast.parse(f if isinstance(f, str) else inspect.getsource(f))
        fun = ast2ast(fun_ast.body[0])

        fun_name, args, fun_ret, exps = translate_ast(fun, types, defs)
        original_f = eval(fun_name) if isinstance(f, str) else f

        # Remove unnecessary expressions
        exps = remove_const_exps(exps, fun_ret)
        exps = remove_unnecessary_assigns(exps)
        exps = merge_unnecessary_assigns(exps)
        # exps = subsitute_exps(exps, fun_ret)

        # Return the qlassf object
        qf = QlassF(fun_name, original_f, args, fun_ret, exps)
        if to_compile:
            qf.compile()
        return qf


def qlassf(
    f: Union[str, Callable],
    types: List[Qtype] = [],
    defs: List[QlassF] = [],
    to_compile: bool = True,
) -> QlassF:
    """Decorator / function creating a QlassF object

    Args:
        f (Union[str, Callable]): the function to be parsed, as a str code or callable
        types (List[Qtype]): list of qtypes to inject
        to_compile (boolean, optional): if True, compile to quantum circuit (default: True)
        defs (List[Qlassf]): list of qlassf to inject
    """
    defs_fun = list(map(lambda q: q.to_logicfun(), defs))

    return QlassF.from_function(f, types, defs_fun, to_compile)
