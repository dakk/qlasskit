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

import inspect
import random
from typing import Tuple, get_args

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from sympy.logic.boolalg import gateinputcount

from qlasskit import Qint, QlassF, Qtype, compiler, const_to_qtype

COMPILATION_ENABLED = True

ENABLED_COMPILERS = [("internal",)]

try:
    import tweedledum

    ENABLED_COMPILERS.append(("tweedledum",))
except:
    pass

try:
    from pyqrack import qrack_simulator
    from qiskit.providers.qrack import Qrack

    qsk_simulator = Qrack.get_backend("qasm_simulator")
except:
    qsk_simulator = Aer.get_backend("aer_simulator")


def inject_parameterized_compilers(params):
    param_inj = []
    for comp in ENABLED_COMPILERS:
        for par in params:
            param_inj.append(tuple(list(par) + [comp[0]]))

    return param_inj


def test_not(a: bool) -> bool:
    return not a


class Qint3(Qint):
    BIT_SIZE = 3


def test_qint3(a: Qint3) -> bool:
    return not a[0]


def qiskit_measure_and_count(circ, shots=1):
    circ.measure_all()
    circ = transpile(circ, qsk_simulator)
    result = qsk_simulator.run(circ, shots=shots).result()
    counts = result.get_counts(circ)
    return counts


def compute_result_of_qcircuit(cls, qf, truth_line):
    """Simulate the quantum circuit for a given truth_line containing inputs"""
    circ = qf.circuit()
    gate = qf.gate()
    qc = QuantumCircuit(gate.num_qubits)

    # Prepare inputs
    [qc.initialize(1 if truth_line[i] else 0, i) for i in range(qf.input_size)]

    qc.append(gate, list(range(qf.num_qubits)))

    # print(qc.decompose().draw("text"))

    # Measure
    counts = qiskit_measure_and_count(qc)

    res = list(counts.keys())[0][::-1]

    if len(res) < qc.num_qubits:
        res += "0" * (qc.num_qubits - len(res))

    res_str = ""
    for qname in qf.truth_table_header()[-qf.ret_size :]:
        res_str += res[circ.qubit_map[qname]]

    cls.assertEqual(len(counts), 1)

    max_qubits = (
        qf.input_size
        + len(qf.expressions)
        + sum([gateinputcount(compiler.optimizer(e[1])) for e in qf.expressions])
    )

    cls.assertLessEqual(qf.gate().num_qubits, max_qubits)

    return res_str


def compute_result_of_originalf(cls, qf, truth_line):
    """Compute the result of originalf for a given truth_line containing inputs"""

    def truth_to_arg(truth, i, argtt):
        """Translate a bin string truth starting from i, to type argtt"""
        if argtt == bool:
            return truth[i], i + 1
        elif inspect.isclass(argtt) and issubclass(argtt, Qtype):
            return (
                argtt.from_bool(truth[i : i + argtt.BIT_SIZE]),
                i + argtt.BIT_SIZE,
            )
        else:  # A tuple
            al = []
            for x in get_args(argtt):
                a, i = truth_to_arg(truth, i, x)
                al.append(a)
            return tuple(al), i

    def res_to_str(res):
        """Translate res to a binary string"""
        if type(res) == bool:
            return "1" if res else "0"
        elif type(res) == tuple:
            return "".join([res_to_str(x) for x in res])
        elif type(res) == int:
            qc = const_to_qtype(res)
            qi = qf.returns.ttype.from_bool(qc[1])
            return qi.to_bin()
        else:
            return res.to_bin()

    args = []
    i = 0
    for x in qf.args:
        arg, i = truth_to_arg(truth_line, i, x.ttype)
        args.append(arg)

    cls.assertEqual(i, qf.input_size)

    res_original = qf.original_f(*args)
    res_original_str = res_to_str(res_original)
    # print(args, res_original, res_original_str, truth_line)
    # print (qf.expressions)

    cls.assertEqual(len(res_original_str), qf.ret_size)
    return res_original_str


def compute_and_compare_results(cls, qf, test_original_f=True):
    """Create and simulate the qcircuit, and compare the result with the
    truthtable and with the original_f"""
    MAX_Q_SIM = 64
    MAX_C_SIM = 2**9
    qc_truth = None

    truth_table = qf.truth_table(MAX_C_SIM)

    if len(truth_table) > MAX_C_SIM:
        truth_table = [random.choice(truth_table) for x in range(MAX_C_SIM)]

    if len(truth_table) > MAX_Q_SIM and COMPILATION_ENABLED:
        qc_truth = [random.choice(truth_table) for x in range(MAX_Q_SIM)]
    elif COMPILATION_ENABLED:
        qc_truth = truth_table

    # circ_qi = qf.circuit().export("circuit", "qiskit")
    # print(qf.expressions)
    # print(circ_qi.draw("text"))

    for truth_line in truth_table:
        # Extract str of truthtable and result
        truth_str = "".join(
            map(lambda x: "1" if x else "0", truth_line[-qf.ret_size :])
        )

        # Calculate and compare the originalf result
        if test_original_f:
            res_original = compute_result_of_originalf(cls, qf, truth_line)
            cls.assertEqual(truth_str, res_original)

        # Calculate and compare the gate result
        if qc_truth and truth_line in qc_truth and COMPILATION_ENABLED:
            res_qc = compute_result_of_qcircuit(cls, qf, truth_line)
            cls.assertEqual(truth_str, res_qc)
