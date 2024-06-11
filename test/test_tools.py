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

import sympy
from sympy.logic.boolalg import is_cnf, is_dnf, is_nnf

# from sympy.logic.boolalg import to_anf
from sympy.logic.utilities.dimacs import load

import qlasskit
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

    def test_help(self):
        result = self.run_command(["python", "-m", "qlasskit.tools.py2bexp", "--help"])
        print(result.stdout)

    def test_version(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2bexp", "--version"]
        )
        print(result.stdout)
        assert result.stdout == f"qlasskit {qlasskit.__version__}\n"

    def test_output_to_stdout(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2bexp", "-i", self.temp_file.name]
        )
        print(result.stdout)
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        assert expr.equals(expected)

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
        print(result.stdout)
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("~b")
        assert expr.equals(expected)

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
                print(content)
                expr = sympy.parse_expr(content)
                expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
                assert expr.equals(expected)
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
        print(result.stdout)
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        assert expr.equals(expected)
        assert is_dnf(result.stdout)

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
        print(result.stdout)
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        assert expr.equals(expected)
        assert is_cnf(result.stdout)

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
        print(result.stdout)
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        assert expr.equals(expected)
        assert is_nnf(result.stdout)

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
        print(result.stdout)
        expr = sympy.parse_expr(result.stdout)
        print(expr)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        assert expr.equals(expected)
        # assert is_anf(result.stdout) # This is not working

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
        print(result.stdout)
        expr = load(result.stdout)
        print(expr)
        # expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        # assert expr.equals(expected)
        self.assertIn("p cnf 3 2", result.stdout)

    def test_stdin_input(self):
        result = self.run_command(
            ["python", "-m", "qlasskit.tools.py2bexp"], stdin_input=dummy_script
        )
        print(result.stdout)
        expr = sympy.parse_expr(result.stdout)
        expected = sympy.parse_expr("(x | y | ~z) & (z | ~y)")
        assert expr.equals(expected)
