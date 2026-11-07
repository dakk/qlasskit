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
        return interpret_as_qtype(istr, self.f.args[0].ttype, len(self.f.args[0]))  # type: ignore
