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

from typing import List, Tuple, Union

from ..qcircuit import QCircuit
from ..qlassfun import QlassF
from ..types import Qtype, interpret_as_qtype
from .qalgorithm import QAlgorithm


class Simon(QAlgorithm):
    def __init__(
        self,
        f: QlassF,
    ):
        """
        Args:
            f (QlassF): our f(x)
        """
        if len(f.args) != 1:
            raise Exception("f should receive exactly one parameter")

        self.f: QlassF = f
        self.search_space_size = len(f.args[0])
        self._qcircuit = QCircuit(self.f.num_qubits, name=f"simon_{f.name}")

        # State preparation
        self._qcircuit.barrier(label="s")
        for i in range(self.search_space_size):
            self._qcircuit.h(i)

        # Prepare and add the f
        self._qcircuit.barrier(label="f")
        self._qcircuit += self.f.circuit()

        # State preparation out
        self._qcircuit.barrier(label="s")
        for i in range(self.search_space_size):
            self._qcircuit.h(i)

    # @override
    @property
    def output_qubits(self) -> List[int]:
        """Returns the list of output qubits"""
        len_a = len(self.f.args[0])
        return list(range(len_a))

    # @override
    def decode_output(
        self, istr: Union[str, int, List[bool]]
    ) -> Union[bool, Tuple, Qtype]:
        return interpret_as_qtype(istr, self.f.args[0].ttype, len(self.f.args[0]))
