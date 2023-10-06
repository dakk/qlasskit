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
- [x] Int: comparison - eq

#### Typechecker branch
- [x] Translate_expr should returns ttype*expr
- [x] Args should also hold the original type
- [x] Transform Env to a class holding also the original types
- [x] Typecheck all the expressions

### Week 3: (9 Oct 23)
- [ ] Int: comparison - >, <, <=, >=, !=
- [ ] Qubit garbage uncomputing and recycling
- [ ] Test: add qubit usage check
- [ ] Compiler: remove consecutive X gates
- [ ] Int arithmetic expressions
- [ ] Properly render documentation

### Week 4: (16 Oct 23)
- [ ] Ast2logic: fixed size loops unrolling

## Month 2: 

### Week 1: (23 Oct 23)
- [ ] Parametrized qlassf

### Week 2: (30 Oct 23)
### Week 3: (6 Nov 23)

### Week 4: (13 Nov 23)

- [ ] First beta release


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

### Language support

- [ ] Ast2logic: if-then-else statement
- [ ] Datatype: Integer
- [ ] Integer comparators
- [ ] Integer constant
- [ ] Integer operations
- [ ] Datatype: List
- [ ] Datatype: Dict
- [ ] Datatype: Fixed
- [ ] Datatype: Enum
- [ ] While loop
- [ ] For loop
- [ ] Recursion
- [ ] Parameter bind

### Abstraction support

- [ ] Combine two QlassF (__add__)
- [ ] Extract boolean expressions from quantum circuits

### Framwork support

- [x] Qiskit
- [ ] QASM
- [ ] QuTip
- [ ] Pennylane
- [ ] Cirq
- [ ] Sympy quantum computing expressions

### Tools

- [ ] py2qasm tools