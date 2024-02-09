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

BQMFormat = Literal["bqm", "ising", "qubo", "pq_model"]
BQMFormats = list(get_args(BQMFormat))

def to_bqm(
    args,
    returns,
    exprs, 
    fmt: BQMFormat
):
    try:
        import pyqubo
    except:
        raise Exception("Library pyqubo not found: run `pip install pyqubo`")
    
    # vars = ['a.0', 'a.1', 'a.2', 'a.3']
    # al = [ Binary(s) for s in vars ]
    # e = AndConst(al[0], And(Not(al[1]), And(al[2], Not(al[3]))), Binary("_ret"), '_ret')
    # model = e.compile()
    
    if fmt == 'bqm':
        return model.to_bqm()
    elif fmt == 'ising':
        return model.to_ising()
    elif fmt == 'qubo':
        return model.to_qubo()
    elif fmt == 'pq_model':
        return model
    else:
        raise Exception(f"Unknown format `{fmt}")    
    