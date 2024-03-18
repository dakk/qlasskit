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
# isort:skip_file

from typing import Literal, get_args  # noqa: F401

SupportedFramework = Literal["qiskit", "sympy", "cirq", "qasm", "pennylane", "qutip"]
SupportedFrameworks = list(get_args(SupportedFramework))

from . import gates  # noqa: F401, E402
from .qcircuit import QCircuit  # noqa: F401, E402
from .qcircuitenhanced import QCircuitEnhanced  # noqa: F401, E402
from .qcircuitwrapper import QCircuitWrapper, reindex  # noqa: F401, E402
from .cnotsim import CNotSim, GateNotSimulableException  # noqa: F401, E402
