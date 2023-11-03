from matplotlib import pyplot as plt
from qiskit import QuantumCircuit

from qlasskit import Qint2, Qint8, Qlist, qlassf


@qlassf
def very_big(a_list: Qlist[Qint8, 8], q_check: Qint8) -> Qint8:
    n = 0
    for el in a_list:
        n += el - q_check
    return n


# very_big.compile('tweedledum')
print(very_big)
print(very_big.circuit().draw())
