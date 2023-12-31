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

import unittest
from typing import Dict

from parameterized import parameterized, parameterized_class
from sympy import Symbol
from sympy.logic.boolalg import Boolean

from qlasskit import qlassf  # QCircuit,
from qlasskit.ast2logic.typing import BoolExpList

# from qlasskit.boolopt import defaultOptimizer
from qlasskit.boolopt.bool_optimizer import custom_simplify_logic  # apply_cse,
from qlasskit.decompiler import Decompiler

from .utils import ENABLED_COMPILERS, compute_and_compare_results


def _merge_expressions(
    exps: BoolExpList, emap: Dict[Symbol, Boolean] = {}
) -> BoolExpList:
    n_exps = []

    for s, e in exps:
        e = e.xreplace(emap)
        e = custom_simplify_logic(e)

        if s.name[0:4] != "_ret":
            emap[s] = e
        else:
            n_exps.append((s, e))

    return n_exps


# TODO: fix for tweedledum
@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestDecompiler(unittest.TestCase):
    @parameterized.expand(
        [
            ("def test(a: bool) -> bool:\n\treturn not a", True),
            ("def test(a: bool) -> bool:\n\treturn True if a else False", True),
            ("def test(a: bool, b: bool) -> bool:\n\tc = a and b\n\treturn c", True),
            ("def test(a: bool, b: bool) -> bool:\n\treturn a | b", True),
        ]
    )
    def test_decompilation(self, f, exact):
        qf = qlassf(f, to_compile=True)  # , compiler=self.compiler)

        dc = Decompiler().decompile(qf.circuit())

        if exact:
            self.assertEqual(len(dc), 1)
            self.assertEqual(len(dc[0].expressions), len(qf.expressions))

        # Set False values for initialization
        _rets = {}
        for s in qf.returns.bitvec:
            _rets[Symbol(s)] = False
        for s in ["anc_0", "anc_1"]:
            _rets[Symbol(s)] = False

        dc0_exps = _merge_expressions(dc[0].expressions, _rets)

        if exact:
            for orig, decomp in zip(qf.expressions, dc0_exps):
                self.assertEqual(orig, decomp)

        # Test functionality
        qf2 = qlassf(f, to_compile=False)
        qf2.expressions = dc0_exps
        qf2.compile(compiler=self.compiler)
        compute_and_compare_results(self, qf2)
        compute_and_compare_results(self, qf)

        # print(dc0_exps, qf.expressions)
        # qf2.circuit().draw()
        # qf.circuit().draw()


def _merge_expressions2(
    exps: BoolExpList, emap: Dict[Symbol, Boolean] = {}
) -> BoolExpList:
    n_exps = []

    for s, e in exps:
        e = e.xreplace(emap)

        emap[s] = e
        n_exps.append((s, e))

    return n_exps


# class TestDecopt(unittest.TestCase):
#     def test_wip(self):
#         f = "def f1(b: bool, n: Qint2) -> Qint2:\n\treturn n + (1 if b else 2)"
#         qf = qlassf(f, to_compile=True)

#         qc = QCircuit(qf.num_qubits * 2 - 1)
#         for i in range(3):
#             qc.append_circuit(qf.circuit(), [0] + list(range(1 + i * 2, 5 + i * 2)))

#         qc["b"] = 0
#         qc["n.0"] = 1
#         qc["n.1"] = 2
#         qc["_ret.0"] = qf.num_qubits * 2 - 3
#         qc["_ret.1"] = qf.num_qubits * 2 - 2

#         init_set = {Symbol("_ret.0"): False, Symbol("_ret.1"): False}
#         for i in range(3, qf.num_qubits * 2 - 3):
#             init_set[Symbol(f"q{i}")] = False

#         print(init_set, qc.qubit_map)

#         dc = Decompiler().decompile(qc)
#         qc.draw()
#         # print(dc)
#         exps = dc[0].expressions
#         exps = _merge_expressions2(exps, init_set)
#         print(exps)
#         #exps = apply_cse(exps)
#         exps = defaultOptimizer.apply(exps)
#         print(exps)  # , qf.expressions)

#         # exps = list(filter(lambda se: se[0].name[0:4] == "_ret", exps))
#         print(exps)

#         print("original was", qf.expressions)

#         qf.expressions = exps
#         qf.compile(uncompute=False)
#         qf.circuit().draw()
#         # compute_and_compare_results(self, qf)


#         f = ("def f_comp(b: bool, n: Qint2) -> Qint2:\n\tfor i in range(3):"
#              "\n\t\tn += (1 if b else 2)\n\treturn n")
#         qf = qlassf(f, to_compile=True)
#         qf.circuit().draw()
#         compute_and_compare_results(self, qf)
#         print("original was", qf.expressions)
