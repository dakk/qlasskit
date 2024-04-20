# Copyright 2023-2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    (tfd, tfpath) = tempfile.mkstemp(prefix="qlassf_", suffix=".py", text=True)

    with open(tfpath, "w") as tf:
        tf.write(scode)

    return parse_file(tfpath)
