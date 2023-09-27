from qiskit import QuantumCircuit

from qlasskit import Int4, qlassf


@qlassf
def f(n: Int4) -> bool:
    if n == 3:
        return True
    else:
        return False


qc = QuantumCircuit(f.num_qubits)
qc.append(f.gate(), f.qubits(0))
