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
from typing import Callable, Dict, List, Tuple, Union, get_args  # noqa: F401

from sympy import Symbol

from .ast2ast import ast2ast
from .ast2logic import Arg, Args, BoolExpList, LogicFun, flatten, translate_ast
from .boolopt import BoolOptimizerProfile, defaultOptimizer
from .boolopt.bool_optimizer import merge_expressions
from .boolquant import Q  # noqa: F403, F401
from .compiler import SupportedCompiler, to_quantum
from .qcircuit import QCircuitWrapper
from .types import *  # noqa: F403, F401
from .types import Qtype, format_outcome, interpret_as_qtype, type_repr

MAX_TRUTH_TABLE_SIZE = 20


class QlassF(QCircuitWrapper):
    """Class representing a qlassf function"""

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

    def __repr__(self):
        ret_str = type_repr(self.returns.ttype)
        arg_str = ", ".join(
            map(lambda arg: f"{arg.name}:{type_repr(arg.ttype)}", self.args)
        )
        exp_str = "\n\t".join(map(lambda exp: f"{exp[0]} = {exp[1]}", self.expressions))
        return f"QlassF<{self.name}>({arg_str}) -> {ret_str}:\n\t{exp_str}"

    # @ovveride
    @property
    def output_size(self):
        """Return the size of the return type (in bits)"""
        return len(self.returns)

    # @ovveride
    @property
    def input_qubits(self) -> List[int]:
        """Returns the list of input qubits"""
        return list(range(reduce(lambda a, b: a + len(b), self.args, 0)))

    # @ovveride
    @property
    def output_qubits(self) -> List[int]:
        """Returns the list of output qubits"""
        return [self._qcircuit.qubit_map[i] for i in self.returns.bitvec]

    # @ovveride
    def encode_input(self, *qvals):
        def val_to_bin(argt, val):
            if argt == bool:
                return "1" if val else "0"
            elif inspect.isclass(argt) and issubclass(argt, Qtype):
                return val.to_bin()
            else:  # A tuple
                al = ""
                for a, i in zip(get_args(argt), val):
                    v = val_to_bin(a, i)
                    al += v
                return al

        vl = ""
        for arg, val in zip(self.args, qvals):
            vl += val_to_bin(arg.ttype, val)
        return vl[::-1]  # TODO: we need an endianess paramter

    # @ovveride
    def decode_output(
        self, istr: Union[str, int, List[bool]]
    ) -> Union[bool, Tuple, Qtype]:
        fcome = format_outcome(istr)[::-1]  # TODO: we need an endianess paramter
        return interpret_as_qtype(fcome[::-1], self.returns.ttype, len(self.returns))

    def __add__(self, qf2) -> "QlassF":
        """Adds two qlassf and return the combination f + g = f(g())"""
        raise Exception("not implemented")

    def truth_table_header(self) -> List[str]:
        """Returns the list of string containing the truth table header"""
        header = flatten(list(map(lambda a: a.bitvec, self.args)))
        header.extend(
            [sym.name for (sym, retex) in self.expressions[-self.output_size :]]
        )
        return header

    def truth_table(self, max=None) -> List[List[bool]]:
        """Returns the truth table for the function using the sympy boolean for computing

        Args:
            max (int, optional): if set, return max lines, randomly selected
        """
        truth = []
        arg_bits = flatten(list(map(lambda a: a.bitvec, self.args)))
        bits = len(arg_bits)

        if not max and (bits + self.output_size) > MAX_TRUTH_TABLE_SIZE:
            raise Exception(
                f"Max truth table size reached: {bits + self.output_size} > {MAX_TRUTH_TABLE_SIZE}"
            )

        exps = merge_expressions(self.expressions)

        for i in range(
            0, 2**bits, int(2**bits / max) if max and max < 2**bits else 1
        ):
            bin_str = bin(i)[2:]
            bin_str = "0" * (bits - len(bin_str)) + bin_str
            bin_arr = list(map(lambda c: c == "1", bin_str))
            known = list(zip(arg_bits, bin_arr))

            for ename, exp in exps:
                exp_sub = exp.subs(known)

                known = list(filter(lambda x: x[0] != ename.name, known))
                known.append(
                    (ename.name if isinstance(ename, Symbol) else ename, exp_sub)
                )

            res = list(zip(arg_bits, bin_arr)) + known[-self.output_size :]
            res_clean = list(map(lambda y: y[1], res))
            truth.append(res_clean)

        return truth

    def compile(self, compiler: SupportedCompiler = "internal", uncompute: bool = True):
        self._qcircuit = to_quantum(
            name=self.name,
            args=self.args,
            returns=self.returns,
            exprs=self.expressions,
            compiler=compiler,
            uncompute=uncompute,
        )

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
        compiler: SupportedCompiler = "internal",
        bool_optimizer: BoolOptimizerProfile = defaultOptimizer,
        uncompute: bool = True,
    ) -> "QlassF":
        """Create a QlassF from a function or a string containing a function

        Args:
            f (Union[str, Callable]): the function to be parsed, as a str code or callable
            types (List[Qtype]): list of qtypes to inject
            defs (List[LogicFun]): list of LogicFun to inject
            to_compile (boolean, optional): if True, compile to quantum circuit (default: True)
            compiler (SupportedCompiler, optional): override default compiler (default: internal)
            bool_optimizer (BoolOptimizerProfile, optional): override default optimizer
                (default: defaultOptimizer)
            uncompute (bool, optional): whenever uncompute input qubits during compilation
                (default: True)
        """
        if isinstance(f, str):
            exec(f)

        fun_ast = ast.parse(f if isinstance(f, str) else inspect.getsource(f))
        fun = ast2ast(fun_ast.body[0])

        fun_name, args, fun_ret, exps = translate_ast(fun, types, defs)
        original_f = eval(fun_name) if isinstance(f, str) else f

        exps = bool_optimizer.apply(exps)

        # Return the qlassf object
        qf = QlassF(fun_name, original_f, args, fun_ret, exps)

        if to_compile:
            qf.compile(compiler, uncompute=uncompute)
        return qf


def qlassf(
    f: Union[str, Callable],
    types: List[Qtype] = [],
    defs: List[QlassF] = [],
    to_compile: bool = True,
    compiler: SupportedCompiler = "internal",
    bool_optimizer: BoolOptimizerProfile = defaultOptimizer,
    uncompute: bool = True,
) -> QlassF:
    """Decorator / function creating a QlassF object

    Args:
        f (Union[str, Callable]): the function to be parsed, as a str code or callable
        types (List[Qtype]): list of qtypes to inject
        defs (List[Qlassf]): list of qlassf to inject
        to_compile (boolean, optional): if True, compile to quantum circuit (default: True)
        compiler (SupportedCompiler, optional): override default compiler (default: internal)
        bool_optimizer (BoolOptimizerProfile, optional): override default optimizer
            (default: defaultOptimizer)
        uncompute (bool, optional): whenever uncompute input qubits during compilation
            (default: True)
    """
    defs_fun = list(map(lambda q: q.to_logicfun(), defs))

    return QlassF.from_function(
        f,
        types,
        defs_fun,
        to_compile,
        compiler,
        uncompute=uncompute,
        bool_optimizer=bool_optimizer,
    )


def qlassfa(
    types: List[Qtype] = [],
    defs: List[QlassF] = [],
    to_compile: bool = True,
    compiler: SupportedCompiler = "internal",
    bool_optimizer: BoolOptimizerProfile = defaultOptimizer,
    uncompute: bool = True,
):
    """Decorator with parameters for qlassf"""

    def _inner(fun):
        return qlassf(fun, types, defs, to_compile, compiler, bool_optimizer, uncompute)

    return _inner
