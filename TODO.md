# Todo list

- [x] POC
- [x] Test suite setup
- [x] Integrate tox with linters, unit-tests, typecheck, coverage
- [x] Ast2logic: base structure and boolean expression
- [x] Dummy compiler from expressions to quantum
- [x] Example code
- [x] Ast2logic: assign
- [x] Dummy compiler: compile ite
- [x] Ast2logic: tuple
- [x] Split ast2logic into a directory
- [x] Ast2logic: write a type inference function
- [x] Ast2logic: fix type inference on assign
- [x] Ast2logic: handle multiple result
- [x] Ast2logic: fix ret_type for multiple results
- [x] QlassF: truth table creation
- [x] Quantum circuit abstraction
- [x] Extend testing to compilation
- [x] Poc compiler 2 using qcircuit abstraction
- [x] OpenQASM3 exporter
- [x] Int: comparison - eq, noteq
- [x] Int: comparison - lt, gt, gte, lte
- [x] Translate_expr should returns ttype*expr
- [x] Args should also hold the original type
- [x] Transform Env to a class holding also the original types
- [x] Typecheck all the expressions
- [x] Test circuit and boolexp using the python code as reference
- [x] Qubit garbage uncomputing and recycling
- [x] Test: add qubit usage check
- [x] Parametrize qint tests over bit_size
- [x] Allow constant functions
- [x] Doc: emphatize the compiler flow
- [x] Doc: properly render documentation
- [x] Builtin debug functions: print()
- [x] Fix code structure and typing location
- [x] Extensible type system
- [x] Builtin functions: max(), min(), len()
- [x] Function call (to builtin)
- [x] Int arithmetic: +, -
- [x] Qtype: bitwise not
- [x] Qtype: shift right / left
- [x] Int: subtraction
- [x] Symbol reassign and augassign
- [x] Remove unneccessary expressions
- [x] Remove quantum circuit identities
- [x] For unrolling
- [x] Bitwise xor, or, and
- [x] Integrate tweedledum for compilation
- [x] Aggregate cascading expressions in for unrolling
- [x] Rewrite qcircuit abstraction
- [x] Inner function
- [x] Grover algorithm
- [x] Tuple-tuple comparison
- [x] Multi var assign
- [x] Integrate qrack on test suite
- [x] Test / support on multiple py version >= 3.8
- [x] Fixed size list
- [x] Grover algorithm tests 
- [x] Slideshow for UF midterm
- [x] Builtin functions: sum(), all(), any()
- [x] Bool optimizers test
- [x] Ast2logic: if-then-else statement
- [x] Midterm call
- [x] Bool optimization refactoring
- [x] Cirq exporter
- [x] Qint multiplier
- [x] Allow quantum gates inside sympy expressions
- [x] CNotSim dummy simulator for circuit testing
- [x] Improve exporting utilities
- [x] Publish doc on github
- [x] Documentation
- [x] Qmatrix
- [x] Hash function preimage attack notebook
- [x] Move all examples to doc
- [x] Simon periodicity
- [x] Deutsch-Jozsa
- [x] Improve documentation
- [x] First stable release
- [x] Use cases
- [x] Int arithmetic: mod
- [x] Simon example
- [x] Deutsch-Jozsa example
- [x] Improve performance on big circuits 
- [x] Minor fixes and new release
- [x] Pennylane exporter
- [x] Regression test for qubit number and gates
- [x] Sympy exporter
- [x] QFT and IQFT
- [x] Separate tests in directories
- [x] Circuit decompilation 
- [x] QuTip Support


## Future features

- [ ] Simplification of circuits using boolean expressions decompilation

### Language support

- [ ] Int arithmetic: div
- [ ] Lambda
- [ ] Builtin function: map
- [ ] Datatype: Char
- [ ] Datatype: Dict
- [ ] Datatype: Float
- [ ] Datatype: Enum
- [ ] While loop
- [ ] Recursion
- [ ] Float arithmetic
- [ ] QFT multiplier

### Abstraction support

- [ ] Parameter bind

### Tools

- [ ] py2qasm tool
- [ ] py2boolexp tool


### Experiments

- [ ] Logic2FPGA backend