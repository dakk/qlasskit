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

from typing import Literal, get_args  # noqa: F401

SupportedFramework = Literal["qiskit", "sympy", "cirq", "qasm", "pennylane", "qutip"]
SupportedFrameworks = list(get_args(SupportedFramework))

from . import gates  # noqa: F401, E402
from .qcircuit import QCircuit  # noqa: F401, E402
from .qcircuitenhanced import QCircuitEnhanced  # noqa: F401, E402
from .qcircuitwrapper import QCircuitWrapper, reindex  # noqa: F401, E402
from .cnotsim import CNotSim, GateNotSimulableException  # noqa: F401, E402
