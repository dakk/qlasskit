# Copyright 2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
from typing import Literal, get_args

from sympy import Symbol
from sympy.logic import And, Not, Or, Xor
from sympy.logic.boolalg import BooleanFalse, BooleanTrue

from .boolopt.bool_optimizer import merge_expressions
from .types import interpret_as_qtype

BQMFormat = Literal["bqm", "ising", "qubo", "pq_model"]
BQMFormats = list(get_args(BQMFormat))


class SympyToBQM:
    def __init__(self, a_vars):
        self.a_vars = a_vars

    def visit(self, e):
        import pyqubo

        if isinstance(e, Symbol):
            return self.a_vars[e.name]
        elif isinstance(e, BooleanFalse):
            return False
        elif isinstance(e, BooleanTrue):
            return True
        elif isinstance(e, Not):
            args = [self.visit(a) for a in e.args]
            return pyqubo.Not(*args)
        elif isinstance(e, And):
            args = [self.visit(a) for a in e.args]

            if len(args) > 2:
                return pyqubo.And(args[0], self.visit(And(*e.args[1:])))
            else:
                return pyqubo.And(*args)
        elif isinstance(e, Xor):
            args = [self.visit(a) for a in e.args]

            if len(args) > 2:
                return pyqubo.Xor(args[0], self.visit(Xor(*e.args[1:])))
            else:
                return pyqubo.Xor(*args)
        elif isinstance(e, Or):
            args = [self.visit(a) for a in e.args]
            return pyqubo.Or(*args)
        else:
            raise Exception(f"{e}: unable to translate to BQM")


def to_bqm(args, returns, exprs, fmt: BQMFormat):  # noqa: C901
    try:
        from pyqubo import AndConst, Binary, NotConst, OrConst, XorConst
    except:
        raise Exception("Library pyqubo not found: run `pip install pyqubo`")

    a_vars = {}
    for arg in args:
        for b in arg.bitvec:
            a_vars[b] = Binary(b)

    exprs = merge_expressions(exprs)

    e = None
    for sym, exp in exprs:
        a_vars[sym.name] = Binary(sym.name)
        stbqm = SympyToBQM(a_vars)

        if isinstance(exp, Symbol):
            arg = stbqm.visit(exp)
            new_e = AndConst(
                a_vars[exp.name], a_vars[exp.name], a_vars[sym.name], sym.name
            )
        elif sym.name[0:4] == "_ret":
            new_e = SympyToBQM(a_vars).visit(exp)
        elif isinstance(exp, Not):
            args = [stbqm.visit(a) for a in exp.args]
            new_e = NotConst(args[0], a_vars[sym.name], sym.name)
        elif isinstance(exp, Or):
            args = [stbqm.visit(a) for a in exp.args]
            new_e = OrConst(args[0], args[1], a_vars[sym.name], sym.name)
        elif isinstance(exp, Xor):
            args = [stbqm.visit(a) for a in exp.args]
            new_e = XorConst(args[0], args[1], a_vars[sym.name], sym.name)
        elif isinstance(exp, And):
            args = [stbqm.visit(a) for a in exp.args]
            new_e = AndConst(args[0], args[1], a_vars[sym.name], sym.name)
        else:
            raise Exception(f"Expression not handled: {e}")

        # new_e = SympyToBQM(a_vars).visit(exp)

        if e is None:
            e = new_e
        else:
            e += new_e

    if e is None:
        raise Exception(f"Problem is empty, cannot be compiled to {fmt}")

    model = e.compile()

    if fmt == "bqm":
        return model.to_bqm()
    elif fmt == "ising":
        return model.to_ising()
    elif fmt == "qubo":
        return model.to_qubo()
    elif fmt == "pq_model":
        return model
    else:
        raise Exception(f"Unknown format `{fmt}")


class DecodedSample:
    def __init__(self, energy, sample):
        self.energy = energy
        self.sample = sample

    def __repr__(self):
        return f"DecodedSample({self.energy}, {self.sample})"


def decode_samples(qf, sampleset):
    """Get dimod sampleset and return an high level decoded solution"""
    model = qf.to_bqm("pq_model")
    decoded = model.decode_sampleset(sampleset)

    new_dec = []
    for el in decoded:
        args = {}
        for arg in qf.args:
            bitstr = [
                el.sample[bv] if bv in el.sample else random.randint(0, 1)
                for bv in arg.bitvec
            ]
            args[arg.name] = interpret_as_qtype(bitstr[::-1], arg.ttype, len(arg))

        # bitstr = [ el.sample[bv] for bv in qf.returns.bitvec ]
        # args['_ret'] = interpret_as_qtype(bitstr, qf.returns.ttype, len(qf.returns))

        new_dec.append(DecodedSample(el.energy, args))

    return new_dec
