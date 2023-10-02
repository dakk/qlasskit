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
- [ ] Split ast2logic into a directory
- [x] Ast2logic: write a type inference function
- [x] Ast2logic: fix type inference on assign
- [x] Ast2logic: handle multiple result
- [ ] Ast2logic: fix ret_type for multiple results
- [ ] Extend testing to compilation
- [ ] Type system and type abstraction
- [ ] Compiler: prepare invertible abstraction

### Week 3: (9 Oct 23)
- [ ] Properly render documentation
- [ ] Compiler: logic to invertible translator
- [ ] Compiler: base invertible to qcircuit translator

### Week 4: (16 Oct 23)
- [ ] Invertible representation simplification (to reduce number of garbage wires)
- [ ] Garbage uncomputing and recycling

## Month 2: 

### Week 1: (23 Oct 23)
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
- [ ] Datatype: List
- [ ] Datatype: Dict
- [ ] Datatype: Fixed
- [ ] Datatype: Enum
- [ ] While loop
- [ ] For loop
- [ ] Recursion
- [ ] Parameter bind

### Abstraction support

- [ ] Add two QlassF


### Framwork support

- [ ] Qiskit
- [ ] QuTip
- [ ] Pennylane
- [ ] Cirq
- [ ] Sympy quantum computing expressions