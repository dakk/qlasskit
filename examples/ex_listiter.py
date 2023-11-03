from matplotlib import pyplot as plt
from qiskit import Aer, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram

from qlasskit import Qint4, Qint8, qlassf, Qlist, Qint2
from qlasskit.algorithms import Groover

@qlassf
def my_fun(a_list: Qlist[Qint2, 3]) -> bool:
    su = 0
    for i in range(3):
        su += a_list[i]
    return su > 2 

print (my_fun.expressions)

my_fun.circuit().export().draw(
    "mpl",
    style={"textcolor": "#ffab40", "backgroundcolor": "black", "linecolor": "#444"},
)
plt.show()