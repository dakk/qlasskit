CLI Tools
=========

Qlasskit also offer two cli tools:
- py2bexp: translate python code to boolean expressions
- py2qasm: translate python code to quantum circuits in qasm format


py2bexp
-------

Receives a python script (file or stdin) in input and outputs bool expressions. The python script should 
contain at least one qlassf function.

.. code-block::

    usage: py2bexp [-h] [-i INPUT_FILE] [-e ENTRYPOINT] [-o OUTPUT] [-f {anf,cnf,dnf,nnf}] [-t {sympy,dimacs}] [-v]

    Convert qlassf functions in a Python script to boolean expressions.

    options:
    -h, --help            show this help message and exit
    -i INPUT_FILE, --input-file INPUT_FILE
                            Input file (default: stdin)
    -e ENTRYPOINT, --entrypoint ENTRYPOINT
                            Entrypoint function name
    -o OUTPUT, --output OUTPUT
                            Output file (default: stdout)
    -f {anf,cnf,dnf,nnf}, --form {anf,cnf,dnf,nnf}
                            Expression form (default: sympy)
    -t {sympy,dimacs}, --format {sympy,dimacs}
                            Output format (default: sympy)
    -v, --version         show program's version number and exit



py2qasm
-------

Receives a python script (file or stdin) in input and outputs qasm code. The python script should 
contain at least one qlassf function.

.. code-block::

    usage: py2qasm [-h] [-i INPUT_FILE] [-e ENTRYPOINT] [-o OUTPUT] [-c {internal,tweedledum,recompiler}] [-q {2.0,3.0}]
                [-v]

    Convert qlassf functions in a Python script to qasm code expressions.

    options:
    -h, --help            show this help message and exit
    -i INPUT_FILE, --input-file INPUT_FILE
                            Input file (default: stdin)
    -e ENTRYPOINT, --entrypoint ENTRYPOINT
                            Entrypoint function name
    -o OUTPUT, --output OUTPUT
                            Output file (default: stdout)
    -c {internal,tweedledum,recompiler}, --compiler {internal,tweedledum,recompiler}
                            QASM compiler (default: internal)
    -q {2.0,3.0}, --qasm-version {2.0,3.0}
                            QASM version (default: 3.0)
    -v, --version         show program's version number and exit