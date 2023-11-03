# Roadmap

> And keep an eye to the roadmap. It likes to change

## Month 1

### Week 1: (25 Sept 23)
- [x] POC
- [x] Test suite setup
- [x] Integrate tox with linters, unit-tests, typecheck, coverage
- [x] Ast2logic: base structure and boolean expression
- [x] Dummy compiler from expressions to quantum
- [x] Example code
- [x] Ast2logic: assign
- [x] Dummy compiler: compile ite
- [x] Ast2logic: tuple

### Week 2: (2 Oct 23)
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

#### Typechecker branch
- [x] Translate_expr should returns ttype*expr
- [x] Args should also hold the original type
- [x] Transform Env to a class holding also the original types
- [x] Typecheck all the expressions

### Week 3: (9 Oct 23)
- [x] Test circuit and boolexp using the python code as reference
- [x] Qubit garbage uncomputing and recycling
- [x] Test: add qubit usage check
- [x] Parametrize qint tests over bit_size
- [x] Allow constant functions
- [x] Doc: emphatize the compiler flow
- [x] Doc: properly render documentation
- [x] Builtin debug functions: print()
- [x] Fix code structure and typing location

### Week 4: (16 Oct 23)
- [x] Extensible type system
- [x] Builtin functions: max(), min(), len()
- [x] Function call (to builtin)
- [x] Int arithmetic: +, -
- [x] Qtype: bitwise not
- [x] Qtype: shift right / left
- [x] Int: subtraction

## Month 2: 

### Week 1: (23 Oct 23)
- [x] Symbol reassign and augassign
- [x] Remove unneccessary expressions
- [x] Remove quantum circuit identities
- [x] For unrolling
- [x] Bitwise xor, or, and
- [x] Integrate tweedledum for compilation
- [x] Aggregate cascading expressions in for unrolling
- [x] Rewrite qcircuit abstraction
- [x] Inner function
- [x] Groover algorithm
- [x] Tuple-tuple comparison
- [x] Multi var assign

### Week 2: (30 Oct 23)

- [x] Integrate qrack on test suite
- [x] Test / support on multiple py version >= 3.8
- [x] Fixed size list
- [x] Groover algorithm tests 
- [x] Slideshow for UF midterm
- [x] Builtin functions: sum(), all(), any()
- [x] Bool optimizers test

### Week 3: (6 Nov 23)

- [ ] Midterm call

### Week 4: (13 Nov 23)

## Month 3:

### Week 1: (20 Nov 23)
### Week 2: (27 Nov 23)
### Week 3: (4 Dec 23)
### Week 4: (11 Dec 23)

## Month 4:

### Week 1: (18 Dec 23)
### Week 2: (25 Dec 23)
### Week 3: (1 Jan 24)

### Week 4: (8 Jan 24)

- [ ] First stable release




## Future features


- [ ] Publish doc on github
- [ ] Int arithmetic expressions (*, /, %)
- [ ] Parametrized qlassf
- [ ] Lambda
- [ ] Builtin function: map
- [ ] First beta release

### Language support

- [ ] Ast2logic: if-then-else statement
- [ ] Datatype: Dict
- [ ] Datatype: Fixed
- [ ] Datatype: Enum
- [ ] While loop
- [ ] Recursion
- [ ] Parameter bind

### Abstraction support

- [ ] Extract boolean expressions from quantum circuits

### Framwork support

- [ ] PyQrack (without qiskit provider)
- [ ] QuTip
- [ ] Pennylane
- [ ] Cirq
- [ ] Sympy quantum computing expressions

### Tools

- [ ] py2qasm tool
- [ ] py2boolexp tool


### Experiments

- [ ] Logic2FPGA backend