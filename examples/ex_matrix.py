from matplotlib import pyplot as plt
from qiskit import Aer, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram

from qlasskit import Qint2, Qint4, Qint8, Qmatrix, qlassf
from qlasskit.algorithms import Grover


@qlassf
def my_fun(a_mat: Qmatrix[bool, 3, 3]) -> bool:
    return a_mat[0][1] and a_mat[1][1]


print(my_fun.expressions)

my_fun.circuit().export().draw(
    "mpl",
    style={"textcolor": "#ffab40", "backgroundcolor": "black", "linecolor": "#444"},
)
plt.show()
