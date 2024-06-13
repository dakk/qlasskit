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
from ..types import Qtype, interpret_as_qtype, format_outcome
from .qalgorithm import QAlgorithm


class BernsteinVazirani(QAlgorithm):
    def __init__(
        self,
        f: QlassF,
    ):
        """
        Args:
            f (QlassF): our f(x) -> bool
        """
        if len(f.args) != 1:
            raise Exception("f should receive exactly one parameter")
        if f.returns.ttype != bool:
            raise Exception("f should returns bool")

        self.f: QlassF = f
        self.search_space_size = len(f.args[0])
        self._qcircuit = QCircuit(self.f.num_qubits, name=f"deutsch_{f.name}")

        self._f_circuit = self.f.circuit()

        # State preparation
        self._qcircuit.barrier(label="s")
        for i in range(self.search_space_size):
            self._qcircuit.h(i)
        self._qcircuit.h(self._f_circuit["_ret"])
        self._qcircuit.z(self._f_circuit["_ret"])

        # Prepare and add the f
        self._qcircuit.barrier(label="f")
        self._qcircuit += self._f_circuit

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
        self, istr: Union[str, int, List, dict]
    ) -> Union[Tuple[str, int], Qtype, str]:
        if isinstance(istr, dict):
            # Create a new dictionary to hold the sums of counts for bitstrings with the first bit removed
            summed_counts = {}
            for bitstring, count in istr.items():
                remaining_bitstring = bitstring[1:]
                if remaining_bitstring in summed_counts:
                    summed_counts[remaining_bitstring] += count
                else:
                    summed_counts[remaining_bitstring] = count
            
            # Find the bitstring with the maximum count
            max_key = max(summed_counts, key=summed_counts.get)
            max_count = summed_counts[max_key]
            istr = max_key
        
        # Format the outcome
        format_outcome(istr, len(self.f.args[0]) - 1)
        
        # Return the decoded output and the associated count
        return {istr[::-1]: max_count}

# Make sure to adjust the format_outcome call by subtracting 1 from the length, as we've removed one bit.

        #iq = interpret_as_qtype(istr, self.f.args[0].ttype, len(self.f.args[0]))
        return istr[-len(self.f.args[0]):][::-1]
        #return "Constant" if iq == 0 else "Balanced"
