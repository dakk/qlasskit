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

from ..qcircuit import QCircuit
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
        if element_to_search is not None:
            raise Exception("not implemented yet")

        if len(oracle.args) != 1:
            raise Exception("the oracle should receive exactly one parameter")

        self.oracle: QlassF = oracle
        self.search_space_size = len(self.oracle.args[0])

        if n_iterations is None:
            n_iterations = math.ceil(math.pi / 4.0 * math.sqrt(self.search_space_size))

        self.n_iterations = n_iterations

        self.qc = QCircuit(self.search_space_size)

        # State preparation
        for i in range(self.search_space_size):
            self.qc.h(i)

        # Prepare and add the quantum oracle
        # TODO

        # Uncompute the oracle expect for the result
        # TODO

        # Build the diffuser
        # TODO

        # Apply for n_iterations
        # TODO

    def interpret_output(self, outcome: Union[str, int, List[bool]]) -> Qtype:
        out = format_outcome(outcome)

        if self.oracle.ret_size == 1:
            return out[0]  # type: ignore

        return self.oracle.returns.ttype.from_bool(out)  # type: ignore
