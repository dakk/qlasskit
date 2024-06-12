# Copyright 2023-2024 Davide Gessa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import tempfile
import unittest
from itertools import permutations

import sympy
from sympy.logic.boolalg import And, Not, Or, is_cnf, is_dnf, is_nnf

# from sympy.logic.boolalg import to_anf
from sympy.logic.utilities.dimacs import load

import qlasskit
from qlasskit.qcircuit import exporter_qasm
from qlasskit.qlassfun import qlassf
from qlasskit.tools import utils

dummy_script = """
from qlasskit import qlassf

@qlassf
def a(b: bool) -> bool:
    return not b

@qlassf
def c(x: bool, y: bool, z: bool) -> bool:
    return (x or y or not z) and (not y or z)
"""


class TestTools_utils(unittest.TestCase):
    def test_parse_str(self):
        print(utils.parse_str(dummy_script))


class TestPy2Bexp(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the dummy script
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        self.temp_file.write(dummy_script.encode())
        self.temp_file.close()

    def tearDown(self):
        # Remove the temporary file
        os.unlink(self.temp_file.name)

    def run_command(self, args, stdin_input=None):
        try:
            result = subprocess.run(
                args, input=stdin_input, capture_output=True, text=True, check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(
                f"Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}"
            )
            print(f"Standard output:\n{e.stdout}")
            print(f"Standard error:\n{e.stderr}")
            raise

    # def test_help(self):
    #     result = self.run_command(["python", "-m", "qlasskit.tools.py2bexp", "--help"])

    def test_version(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2bexp", "--version"]
        )
        self.assertTrue(result.stdout == f"qlasskit {qlasskit.__version__}\n")

    def test_output_to_stdout(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2bexp", "-i", self.temp_file.name]
        )
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        self.assertTrue(expr.equals(expected))

    def test_specific_entrypoint(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2bexp",
                "-i",
                self.temp_file.name,
                "-e",
                "a",
            ]
        )
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("~b")
        self.assertTrue(expr.equals(expected))

    def test_output_to_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            output_file = temp_output.name
        try:
            self.run_command(
                [
                    "python",
                    "-m",
                    "qlasskit.tools.py2bexp",
                    "-i",
                    self.temp_file.name,
                    "-o",
                    output_file,
                ]
            )
            with open(output_file, "r") as f:
                content = f.read()
                expr = sympy.parse_expr(content)
                expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
                self.assertTrue(expr.equals(expected))
        finally:
            os.unlink(output_file)

    def test_dnf_form(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2bexp",
                "-i",
                self.temp_file.name,
                "-f",
                "dnf",
            ]
        )
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        self.assertTrue(is_dnf(result.stdout))
        self.assertTrue(expr.equals(expected))

    def test_cnf_form(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2bexp",
                "-i",
                self.temp_file.name,
                "-f",
                "cnf",
            ]
        )
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        self.assertTrue(is_cnf(result.stdout))
        self.assertTrue(expr.equals(expected))

    def test_nnf_form(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2bexp",
                "-i",
                self.temp_file.name,
                "-f",
                "nnf",
            ]
        )
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        self.assertTrue(is_nnf(result.stdout))
        self.assertTrue(expr.equals(expected))

    def test_anf_form(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2bexp",
                "-i",
                self.temp_file.name,
                "-f",
                "anf",
            ]
        )
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        self.assertTrue(expr.equals(expected))
        # self.assertTrue(is_anf(result.stdout)) # This is not working

    def test_dimacs_format(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2bexp",
                "-i",
                self.temp_file.name,
                "-f",
                "cnf",
                "-t",
                "dimacs",
            ]
        )
        expr = load(result.stdout)
        symbols = expr.free_symbols

        # The result should be one of the 6 permutations of the expected expressions
        # because the order of the symbols in the DIMACS format is not guaranteed
        assert_val = False
        for sl in permutations(symbols):
            exp = And(Or(sl[0], sl[1], Not(sl[2])), Or(sl[2], Not(sl[1])))
            if expr.equals(exp):
                assert_val = True
                break

        self.assertTrue(assert_val)
        self.assertIn("p cnf 3 2", result.stdout)

    def test_stdin_input(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2bexp"], stdin_input=dummy_script
        )
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        self.assertTrue(expr.equals(expected))


dummy_qlassf = """
def c(x: bool, y: bool, z: bool) -> bool:
    return (x or y or not z) and (not y or z)
"""


class TestPy2Qasm(unittest.TestCase):

    def setUp(self):
        # Create a temporary file to hold the dummy script
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        self.temp_file.write(dummy_script.encode())
        self.temp_file.close()

    def tearDown(self):
        # Remove the temporary file
        os.unlink(self.temp_file.name)

    def run_command(self, args, stdin_input=None):
        try:
            result = subprocess.run(
                args, input=stdin_input, capture_output=True, text=True, check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(
                f"Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}"
            )
            print(f"Standard output:\n{e.stdout}")
            print(f"Standard error:\n{e.stderr}")
            raise

    # def test_help(self):
    #     result = self.run_command(["python", "-m", "qlasskit.tools.py2qasm", "--help"])

    def test_version(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2qasm", "--version"]
        )
        self.assertTrue(result.stdout == f"qlasskit {qlasskit.__version__}\n")

    def test_output_to_stdout(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2qasm", "-i", self.temp_file.name]
        )
        print(result.stdout)
        qf = qlassf(dummy_qlassf, to_compile=True, compiler="internal")
        exporter = exporter_qasm.QasmExporter(version=3)
        expected = exporter.export(qf.circuit(), mode="circuit") + "\n"
        print(expected)
        self.assertTrue(result.stdout == expected)

    def test_specific_entrypoint(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2qasm",
                "-i",
                self.temp_file.name,
                "-e",
                "a",
            ]
        )
        print(result.stdout)
        qf = qlassf(
            "def a(b: bool) -> bool:\n\treturn not b",
            to_compile=True,
            compiler="internal",
        )
        exporter = exporter_qasm.QasmExporter(version=3)
        expected = exporter.export(qf.circuit(), mode="circuit") + "\n"
        self.assertTrue(result.stdout == expected)

    def test_output_to_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            output_file = temp_output.name
        try:
            self.run_command(
                [
                    "python",
                    "-m",
                    "qlasskit.tools.py2qasm",
                    "-i",
                    self.temp_file.name,
                    "-o",
                    output_file,
                ]
            )
            with open(output_file, "r") as f:
                content = f.read()
                print(content)
                qf = qlassf(dummy_qlassf, to_compile=True, compiler="internal")
                exporter = exporter_qasm.QasmExporter(version=3)
                expected = exporter.export(qf.circuit(), mode="circuit")
                self.assertTrue(content == expected)
        finally:
            os.unlink(output_file)

    def test_stdin_input(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2qasm"], stdin_input=dummy_script
        )
        print(result.stdout)
        qf = qlassf(dummy_qlassf, to_compile=True, compiler="internal")
        exporter = exporter_qasm.QasmExporter(version=3)
        expected = exporter.export(qf.circuit(), mode="circuit") + "\n"
        self.assertTrue(result.stdout == expected)

    def test_qasm_version_2(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2qasm",
                "-i",
                self.temp_file.name,
                "-q",
                "2.0",
            ]
        )
        print(result.stdout)
        qf = qlassf(dummy_qlassf, to_compile=True, compiler="internal")
        exporter = exporter_qasm.QasmExporter(version=2)
        expected = exporter.export(qf.circuit(), mode="circuit") + "\n"
        self.assertTrue(result.stdout == expected)

    def test_qasm_version_3(self):
        result = self.run_command(
            [
                "python",
                "-m",
                "qlasskit.tools.py2qasm",
                "-i",
                self.temp_file.name,
                "-q",
                "3.0",
            ]
        )
        print(result.stdout)
        qf = qlassf(dummy_qlassf, to_compile=True, compiler="internal")
        exporter = exporter_qasm.QasmExporter(version=3)
        expected = exporter.export(qf.circuit(), mode="circuit") + "\n"
        self.assertTrue(result.stdout == expected)
