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

from typing import Literal, get_args

from .expqmap import ExpQMap  # noqa: F401
from .compiler import Compiler, CompilerException  # noqa: F401

try:
    import tweedledum  # noqa: F401

    TWEEDLEDUM_ENABLED = True
except:
    TWEEDLEDUM_ENABLED = False

from .internalcompiler import InternalCompiler  # noqa: E402

if TWEEDLEDUM_ENABLED:
    from .tweedledumcompiler import TweedledumCompiler


SupportedCompiler = Literal["internal", "poc3", "tweedledum"]
SupportedCompilers = list(get_args(SupportedCompiler))

if not TWEEDLEDUM_ENABLED:
    SupportedCompilers.remove("tweedledum")


def to_quantum(
    name,
    args,
    returns,
    exprs,
    compiler: SupportedCompiler = "internal",
    uncompute: bool = True,
):
    sel_compiler: Compiler

    if compiler == "internal":
        sel_compiler = InternalCompiler()
    elif compiler == "tweedledum" and TWEEDLEDUM_ENABLED:
        sel_compiler = TweedledumCompiler()
    else:
        raise Exception(
            f"Compiler {compiler} not supported. Choose one between {SupportedCompilers}"
        )

    circ = sel_compiler.compile(name, args, returns, exprs, uncompute)
    return circ
