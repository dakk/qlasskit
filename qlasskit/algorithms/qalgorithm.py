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

from typing import Any, Dict, List, Union

from ..qcircuit import QCircuit, SupportedFramework


def format_outcome(out: Union[str, int, List[bool]]) -> List[bool]:
    if isinstance(out, str):
        return [True if c == "1" else False for c in out]
    elif isinstance(out, int):
        return format_outcome(str(bin(out))[2:])
    elif isinstance(out, List):
        return out
    raise Exception("Invalid format")


class QAlgorithm:
    qc: QCircuit

    def __init__(self):
        pass

    def interpret_outcome(self, outcome: Union[str, int, List[bool]]) -> Any:
        """Get the quantum circuit outcome, and return a meaningful data

        Args:
            outcome: the binary string / number to interpret

        Returns:
            Any: the outcome in a meaningful format
        """
        raise Exception("abstract")

    def out_qubits(self) -> List[int]:
        """Returns a list of output qubits"""
        raise Exception("abstract")

    def interpet_counts(self, counts: Dict[str, int]) -> Dict[Any, int]:
        """Interpet data inside a circuit counts dict"""
        l = [(self.interpret_outcome(e), c) for (e, c) in counts.items()]
        d = {}
        for (e, c) in l:
            inter = self.interpret_outcome(e)
            if inter in d:
                d[inter] += c
            else:
                d[inter] = c
        return d

    def export(self, framework: SupportedFramework = "qiskit") -> Any:
        """Export the algorithm to a supported framework"""
        return self.qc.export(mode="circuit", framework=framework)
