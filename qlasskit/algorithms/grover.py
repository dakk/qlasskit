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

import math
from typing import List, Optional, Tuple, Union

from ..qcircuit import QCircuit, gates
from ..qlassfun import QlassF
from ..types import Qtype, interpret_as_qtype
from .qalgorithm import QAlgorithm, oraclize


class Grover(QAlgorithm):
    def __init__(
        self,
        oracle: QlassF,
        element_to_search: Optional[Qtype] = None,
        n_iterations: Optional[int] = None,
        n_matching: int = 1,
    ):
        """
        Args:
            oracle (QlassF): our f(x) -> bool that returns True if x satisfies the function or
                a generic function f(x) = y that we want to compare with element_to_search
            element_to_search (Qtype, optional): the element we want to search
            n_iterations (int, optional): force a number of iterations
                (otherwise, pi/4*sqrt(N/n_matching))
            n_matching (int): the number of expected matching values (default: 1)
        """
        if len(oracle.args) != 1:
            raise Exception("the oracle should receive exactly one parameter")

        self.oracle: QlassF
        self.n_matching = n_matching
        self.search_space_size = len(oracle.args[0])

        if n_iterations is None:
            n_iterations = math.ceil(
                math.pi / 4.0 * math.sqrt(2**self.search_space_size / self.n_matching)
            )

        self.n_iterations = n_iterations

        self._qcircuit = QCircuit(self.search_space_size, name=f"grover__{oracle.name}")

        # State preparation
        for i in range(self.search_space_size):
            self._qcircuit.h(i)

        # Prepare and add the quantum oracle
        if element_to_search is not None:
            self.oracle = oraclize(oracle, element_to_search)
        else:
            self.oracle = oracle

        oracle_qc = self.oracle.circuit()

        # Add negative phase to result
        oracle_qc.add_qubit(name="_ret_phased")
        oracle_qc.mctrl(gates.Z(), [oracle_qc["_ret"]], oracle_qc["_ret_phased"])

        # Build the diffuser
        diffuser_qc = QCircuit(oracle_qc.num_qubits)
        for i in range(self.search_space_size):
            diffuser_qc.h(i)
            diffuser_qc.x(i)
        diffuser_qc.h(oracle_qc["_ret_phased"])
        diffuser_qc.x(oracle_qc["_ret_phased"])

        diffuser_qc.mctrl(
            gates.Z(), list(range(self.search_space_size)), oracle_qc["_ret_phased"]
        )

        for i in range(self.search_space_size):
            diffuser_qc.x(i)
            diffuser_qc.h(i)
        diffuser_qc.x(oracle_qc["_ret_phased"])
        diffuser_qc.h(oracle_qc["_ret_phased"])

        # Apply for n_iterations
        [
            self._qcircuit.add_qubit()
            for i in range(oracle_qc.num_qubits - self.search_space_size)
        ]
        self._qcircuit.h(oracle_qc["_ret_phased"])

        # Repeat oracle and diffuser for n_iterations
        self._qcircuit += (oracle_qc + diffuser_qc).repeat(n_iterations)

    # @override
    @property
    def output_qubits(self) -> List[int]:
        """Returns the list of output qubits"""
        len_a = len(self.oracle.args[0])
        return list(range(len_a))

    # @override
    def decode_output(
        self, istr: Union[str, int, List[bool]]
    ) -> Union[bool, Tuple, Qtype]:
        return interpret_as_qtype(
            istr, self.oracle.args[0].ttype, len(self.oracle.args[0])
        )
