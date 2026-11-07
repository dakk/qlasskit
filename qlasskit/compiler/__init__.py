# Copyright (C) 2023-2026 Davide Gessa
# This file is part of Qlasskit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# isort:skip_file

from typing import Literal, List, get_args

from .expqmap import ExpQMap  # noqa: F401
from .compiler import Compiler, CompilerException  # noqa: F401
from ..ast2logic.typing import Arg, Args, BoolExpList

try:
    import tweedledum  # noqa: F401

    TWEEDLEDUM_ENABLED = True
except:
    TWEEDLEDUM_ENABLED = False

from .internalcompiler import InternalCompiler  # noqa: E402
from .recompiler import ReCompiler  # noqa: E402

if TWEEDLEDUM_ENABLED:
    from .tweedledumcompiler import TweedledumCompiler


SupportedCompiler = Literal["internal", "recompiler", "tweedledum"]
SupportedCompilers = list(get_args(SupportedCompiler))

if not TWEEDLEDUM_ENABLED:
    SupportedCompilers.remove("tweedledum")


def to_quantum(
    name: str,
    args: Args,
    returns: Arg,
    exprs: BoolExpList,
    compiler: SupportedCompiler = "internal",
    uncompute: bool = True,
):
    sel_compiler: Compiler

    if compiler == "internal":
        sel_compiler = InternalCompiler()
    elif compiler == "recompiler":
        sel_compiler = ReCompiler()
    elif compiler == "tweedledum" and TWEEDLEDUM_ENABLED:
        sel_compiler = TweedledumCompiler()
    else:
        raise Exception(
            f"Compiler {compiler} not supported. Choose one between {SupportedCompilers}"
        )

    circ = sel_compiler.compile(name, args, returns, exprs, uncompute)
    return circ


def exprs_to_quantum(
    exprs, symbols: List[str], compiler: SupportedCompiler = "internal"
):
    args = []
    for s in symbols:
        args.append(Arg(s, bool, [s]))
    return to_quantum(
        name="",
        args=args,
        returns=None,  # type: ignore
        exprs=exprs,
        compiler=compiler,
        uncompute=False,
    )
