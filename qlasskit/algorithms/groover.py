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

import math
from typing import List, Optional, Union

from ..qcircuit import QCircuit, gates
from ..qlassf import QlassF
from ..types import Qtype
from .qalgorithm import QAlgorithm, format_outcome


class Groover(QAlgorithm):
    def __init__(
        self,
        oracle: QlassF,
        element_to_search: Qtype,
        n_iterations: Optional[int] = None,
    ):
        """
        Args:
            oracle (QlassF): our f(x) -> bool that returns True if x satisfies the function
            element_to_search (Qtype): the element we want to search
            n_iterations (int, optional): force a number of iterations (otherwise, pi/4*sqrt(N))
        """
        if len(oracle.args) != 1:
            raise Exception("the oracle should receive exactly one parameter")

        self.oracle: QlassF = oracle
        self.search_space_size = len(self.oracle.args[0])

        if n_iterations is None:
            n_iterations = math.ceil(math.pi / 4.0 * math.sqrt(self.search_space_size))

        self.n_iterations = n_iterations

        self.qc = QCircuit(self.search_space_size)

        # State preparation
        self.qc.barrier(label="s")
        for i in range(self.search_space_size):
            self.qc.h(i)

        # Prepare and add the quantum oracle
        if element_to_search is not None:
            argt_name = self.oracle.args[0].ttype.__name__  # type: ignore

            oracle_outer = QlassF.from_function(
                f"""
def oracle_outer(v: {argt_name}) -> bool:
    return {self.oracle.name}(v) == {element_to_search}
""",
                defs=[self.oracle.to_logicfun()],
            )
        else:
            oracle_outer = self.oracle

        oracle_qc = oracle_outer.circuit()

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
            self.qc.add_qubit()
            for i in range(oracle_qc.num_qubits - self.search_space_size)
        ]
        self.qc.h(oracle_qc["_ret_phased"])

        for i in range(n_iterations):
            self.qc.barrier(label=f"g{i}")
            self.qc += oracle_qc.copy()

            self.qc.barrier()
            self.qc += diffuser_qc.copy()

    def circuit(self) -> QCircuit:
        return self.qc

    def out_qubits(self) -> List[int]:
        len_a = len(self.oracle.args[0])
        return list(range(len_a))

    def interpret_outcome(self, outcome: Union[str, int, List[bool]]) -> Qtype:
        out = format_outcome(outcome)

        len_a = len(self.oracle.args[0])
        if len_a == 1:
            return out[0]  # type: ignore

        return self.oracle.args[0].ttype.from_bool(out[::-1][0:len_a])  # type: ignore
