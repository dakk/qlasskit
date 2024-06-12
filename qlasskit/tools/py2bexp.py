#!/usr/bin/env python3

# Copyright 2023-2024 Davide Gessa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys

import sympy
from sympy.logic.boolalg import to_anf, to_cnf, to_dnf, to_nnf

import qlasskit
from qlasskit.qlassfun import QlassF
from qlasskit.tools.utils import parse_str

from .tools import find_last_qlassf


def read_input(input_file):
    if input_file == "-":
        return sys.stdin.read()
    with open(input_file, "r") as file:
        return file.read()


def convert_to_bool_expression(qlassf: QlassF, form: str):
    combined_expr = sympy.And(*[expr[1] for expr in qlassf.expressions])

    if form == "anf":
        return to_anf(combined_expr)
    elif form == "cnf":
        return to_cnf(combined_expr, simplify=True)
    elif form == "dnf":
        return to_dnf(combined_expr, simplify=True)
    elif form == "nnf":
        return to_nnf(combined_expr, simplify=True)
    return combined_expr  # Default case if no specific form is requested


def convert_to_dimacs(expr):
    clauses = to_cnf(expr, simplify=True).args
    if len(clauses) == 1 and isinstance(clauses[0], sympy.Symbol):
        clauses = [clauses]

    var_dict = {symbol: i + 1 for i, symbol in enumerate(expr.free_symbols)}
    dimacs_clauses = []

    for clause in clauses:
        if isinstance(clause, sympy.Or):
            clause_literals = clause.args
        else:
            clause_literals = [clause]

        dimacs_clause = []
        for lit in clause_literals:
            if isinstance(lit, sympy.Not):
                dimacs_clause.append(-var_dict[lit.args[0]])
            else:
                dimacs_clause.append(var_dict[lit])
        dimacs_clauses.append(dimacs_clause)

    num_vars = len(var_dict)
    num_clauses = len(dimacs_clauses)
    dimacs_str = f"p cnf {num_vars} {num_clauses}\n"
    for clause in dimacs_clauses:
        dimacs_str += " ".join(map(str, clause)) + " 0\n"
    return dimacs_str


def output_result(result, output_file, output_format, form):
    if output_format == "dimacs":
        if form != "cnf":
            print(
                "Warning: DIMACS format is only supported for CNF form. Converting to CNF."
            )
            result = to_cnf(result, simplify=True)
        result = convert_to_dimacs(result)
    if output_file == "-":
        print(result)
    else:
        with open(output_file, "w") as file:
            file.write(str(result))


def main():
    parser = argparse.ArgumentParser(
        description="Convert qlassf functions in a Python script to boolean expressions."
    )
    parser.add_argument(
        "-i", "--input-file", default="-", help="Input file (default: stdin)"
    )
    parser.add_argument("-e", "--entrypoint", help="Entrypoint function name")
    parser.add_argument(
        "-o", "--output", default="-", help="Output file (default: stdout)"
    )
    parser.add_argument(
        "-f",
        "--form",
        choices=["anf", "cnf", "dnf", "nnf"],
        default="sympy",
        help="Expression form (default: sympy)",
    )
    parser.add_argument(
        "-t",
        "--format",
        choices=["sympy", "dimacs"],
        default="sympy",
        help="Output format (default: sympy)",
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

    if qlassf:
        bool_expr = convert_to_bool_expression(qlassf, args.form)
        output_result(bool_expr, args.output, args.format, args.form)
    else:
        print("No qlassf function found", file=sys.stderr)


if __name__ == "__main__":
    main()
