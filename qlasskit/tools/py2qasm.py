#!/usr/bin/env python3

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

import argparse
import sys

import qlasskit
from qlasskit.qcircuit import exporter_qasm
from qlasskit.qlassfun import QlassF
from qlasskit.tools.utils import parse_str

from .tools import find_last_qlassf


def read_input(input_file: str):
    if input_file == "-":
        return sys.stdin.read()
    with open(input_file, "r") as file:
        return file.read()


def convert_to_quasm(qlassf: QlassF, compiler="internal", version=3):
    qlassf.compile(compiler=compiler)
    qcirc = qlassf.circuit()
    exporter = exporter_qasm.QasmExporter(version=version)
    return exporter.export(qcirc, mode="circuit")


def output_result(result, output_file: str):
    if output_file == "-":
        print(result)
    else:
        with open(output_file, "w") as file:
            file.write(str(result))


def main():
    parser = argparse.ArgumentParser(
        description="Convert qlassf functions in a Python script to qasm code expressions."
    )
    parser.add_argument(
        "-i", "--input-file", default="-", help="Input file (default: stdin)"
    )
    parser.add_argument("-e", "--entrypoint", help="Entrypoint function name")
    parser.add_argument(
        "-o", "--output", default="-", help="Output file (default: stdout)"
    )
    parser.add_argument(
        "-c",
        "--compiler",
        choices=["internal", "tweedledum", "recompiler"],
        default="internal",
        help="QASM compiler (default: internal)",
    )
    parser.add_argument(
        "-q",
        "--qasm-version",
        choices=["2.0", "3.0"],
        default="3.0",
        help="QASM version (default: 3.0)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"qlasskit {qlasskit.__version__}"
    )

    args = parser.parse_args()

    script = read_input(args.input_file)
    qlassf_list = parse_str(script)

    if args.entrypoint:
        qlassf = next((f[1] for f in qlassf_list if f[0] == args.entrypoint), None)
    else:
        qlassf = find_last_qlassf(qlassf_list)

    compiler = args.compiler
    version = 3 if args.qasm_version == "3.0" else 2

    if qlassf:
        bool_expr = convert_to_quasm(qlassf, compiler=compiler, version=version)
        output_result(bool_expr, args.output)
    else:
        print("No qlassf function found", file=sys.stderr)


if __name__ == "__main__":
    main()
