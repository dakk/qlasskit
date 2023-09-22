from qiskit import QuantumCircuit
from qlasskit import qlassf, Int8, Param

@qlassf
def f(n: Int4, n_it: Param[int]) -> Int8:
  v = 0
  for x in range(n_it):
    v += n
  return n     


f4 = f.bind(n_it=4)
qc = QuantumCircuit(f4.num_qubits)

qc.append(f4.gate, f4.qubits_list(0))