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

import os
import tempfile
from importlib import util as iutil
from inspect import getmembers
from typing import List, Tuple

from .. import QlassF


def parse_file(fpath: str) -> List[Tuple[str, QlassF]]:
    """Same as parse_str, but works with a filepath"""
    mname = os.path.basename(fpath).replace(".py", "")
    spec = iutil.spec_from_file_location(mname, fpath)

    if spec is None:
        raise Exception(f"Unable to load module {mname} from {fpath}")

    md = iutil.module_from_spec(spec)
    spec.loader.exec_module(md)  # type: ignore

    defs = list(filter(lambda x: isinstance(x[1], QlassF), getmembers(md)))
    return defs


def parse_str(scode: str) -> List[Tuple[str, QlassF]]:
    """Given a string `scode` containing a script with qlassf definitions,
    returns a list of qlassf objects"""
    tfd, tfpath = tempfile.mkstemp(prefix="qlassf_", suffix=".py", text=True)

    with open(tfpath, "w") as tf:
        tf.write(scode)

    return parse_file(tfpath)
