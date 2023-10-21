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
# isort:skip_file


from .compiler import Compiler, CompilerException, optimizer  # noqa: F401

from .multipass import MultipassCompiler
from .poccompiler2 import POCCompiler2


def to_quantum(name, args, returns, exprs, compiler="poc2"):
    if compiler == "multipass":
        s = MultipassCompiler()
    elif compiler == "poc2":
        s = POCCompiler2()

    circ = s.compile(name, args, returns, exprs)
    return circ
