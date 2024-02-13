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

from sympy import Symbol
from sympy.logic import Not, And, Xor, Or
from typing import Literal, get_args

BQMFormat = Literal["bqm", "ising", "qubo", "pq_model"]
BQMFormats = list(get_args(BQMFormat))

class SympyToBQM:
    def __init__(self, a_vars):
        self.a_vars = a_vars
        
    def visit(self, e):
        import pyqubo
        
        if isinstance(e, Symbol):
            return self.a_vars[e.name]
        elif isinstance(e, Not):
            args = [ self.visit(a) for a in e.args ]
            return pyqubo.Not(*args)
        elif isinstance(e, And):
            args = [ self.visit(a) for a in e.args ]
            return pyqubo.And(*args)
        elif isinstance(e, Xor):
            args = [ self.visit(a) for a in e.args ]
            return pyqubo.Xor(*args)
        elif isinstance(e, Or):
            args = [ self.visit(a) for a in e.args ]
            return pyqubo.Or(*args)
        else:
            raise Exception(f'{e}: not handled')

    
def to_bqm(args, returns, exprs, fmt: BQMFormat):
    try:
        import pyqubo
    except:
        raise Exception("Library pyqubo not found: run `pip install pyqubo`")
    
    from pyqubo import Binary #, NotConst, AndConst, XorConst, 

    a_vars = {}
    for arg in args:
        for b in arg.bitvec:
            a_vars[b] = Binary(b)           
            
    e = None
    for (sym, exp) in exprs:        
        # TODO: capire se questo e' realmente necessario o se serve solo per 
        # condizioni
        # stbqm = SympyToBQM(a_vars)        
        # if isinstance(exp, Symbol):
        #     arg = stbqm.visit(exp)
        # elif isinstance(exp, Not):
        #     args = [ stbqm.visit(a) for a in e.args ]
        # elif isinstance(exp, Or):
        #     args = [ stbqm.visit(a) for a in e.args ]
        # elif isinstance(exp, Xor):
        #     args = [ stbqm.visit(a) for a in e.args ]
        # elif isinstance(exp, And):
        #     args = [ stbqm.visit(a) for a in e.args ]
            
        new_e = SympyToBQM(a_vars).visit(exp)
        if e is None:
            e = new_e
        else:
            e += new_e
    
    # args = ['a.0', 'a.1', 'a.2', 'a.3']
    # al = [ Binary(s) for s in vars ]
    # e = AndConst(al[0], And(Not(al[1]), And(al[2], Not(al[3]))), Binary("_ret"), '_ret')
    
    model = e.compile()
    # print(e)

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


def decode_samples(qf, sampleset):
    model = qf.to_bqm('pq_model')
    return model.decode_sampleset(sampleset)