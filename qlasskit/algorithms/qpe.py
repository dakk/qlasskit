from typing import List, Union, Tuple
from qlasskit.qcircuit import QCircuit
from qlasskit.qlassfun import QlassF
from qlasskit.types import Qtype, interpret_as_qtype
from qlasskit.algorithms.qalgorithm import QAlgorithm

class QPE(QAlgorithm):
    def __init__(self, unitary: QlassF, eigenvector: QlassF, num_qubits: int):
        """
        Args:
            unitary (QlassF): The unitary operator U whose eigenvalue is to be estimated.
            eigenvector (QlassF): The eigenvector |ψ⟩ of the unitary operator U.
            num_qubits (int): Number of qubits used for phase estimation.
        """
        self.unitary = unitary
        self.eigenvector = eigenvector
        self.num_qubits = num_qubits

        self._qcircuit = QCircuit(num_qubits + self.unitary.num_qubits, name=f"qpe_{unitary.name}")

        # Prepare eigenvector
        self._qcircuit += self.eigenvector.circuit()

        # Apply Hadamard gates to the first num_qubits
        for i in range(num_qubits):
            self._qcircuit.h(i)

        # Apply controlled unitary operations
        for i in range(num_qubits):
            self._qcircuit.append(self.unitary.circuit(), [i] + list(range(num_qubits, num_qubits + self.unitary.num_qubits)))

        # Apply inverse Quantum Fourier Transform
        self._qcircuit.qft(range(num_qubits), inverse=True)

    @property
    def output_qubits(self) -> List[int]:
        """Returns the list of output qubits"""
        return list(range(self.num_qubits))

    def decode_output(
        self, istr: Union[str, int, List[bool]]
    ) -> Union[bool, Tuple, Qtype, str]:
        iq = interpret_as_qtype(istr, self.unitary.args[0].ttype, len(self.unitary.args[0]))
        return f"Phase: {iq / (2 ** self.num_qubits)}"
from typing import List, Union, Tuple
from qlasskit.qcircuit import QCircuit
from qlasskit.qlassfun import QlassF
from qlasskit.types import Qtype, interpret_as_qtype
from qlasskit.algorithms.qalgorithm import QAlgorithm

class QPE(QAlgorithm):
    def __init__(self, unitary: QlassF, eigenvector: QlassF, num_qubits: int):
        """
        Args:
            unitary (QlassF): The unitary operator U whose eigenvalue is to be estimated.
            eigenvector (QlassF): The eigenvector |ψ⟩ of the unitary operator U.
            num_qubits (int): Number of qubits used for phase estimation.
        """
        self.unitary = unitary
        self.eigenvector = eigenvector
        self.num_qubits = num_qubits

        self._qcircuit = QCircuit(num_qubits + self.unitary.num_qubits, name=f"qpe_{unitary.name}")

        # Prepare eigenvector
        self._qcircuit += self.eigenvector.circuit()

        # Apply Hadamard gates to the first num_qubits
        for i in range(num_qubits):
            self._qcircuit.h(i)

        # Apply controlled unitary operations
        for i in range(num_qubits):
            self._qcircuit.append(self.unitary.circuit(), [i] + list(range(num_qubits, num_qubits + self.unitary.num_qubits)))

        # Apply inverse Quantum Fourier Transform
        self._qcircuit.qft(range(num_qubits), inverse=True)

    @property
    def output_qubits(self) -> List[int]:
        """Returns the list of output qubits"""
        return list(range(self.num_qubits))

    def decode_output(
        self, istr: Union[str, int, List[bool]]
    ) -> Union[bool, Tuple, Qtype, str]:
        if isinstance(istr, str):
            phase_binary = istr
        elif isinstance(istr, int):
            phase_binary = bin(istr)[2:].zfill(self.num_qubits)
        elif isinstance(istr, list):
            phase_binary = ''.join(['1' if bit else '0' for bit in istr])
        else:
            raise ValueError("Invalid input type for decode_output")

        phase_int = int(phase_binary, 2)
        phase = phase_int / (2 ** self.num_qubits)
        return f"Phase: {phase}"
