# Qlasskit

Qlasskit is a python library that allow to write classical algorithms in python, and transform them to unitary operators (gates) so they can be used in a quantum circuit.

This should be useful in every algorithm that rely on a 'blackbox' function like Simon, Groover, Deutsch and so on, or in general to descrive classical parts of a quantum algorithm.


```python
@qlassf
def f(n: Int4) -> bool:
  if n == 3:
    return True
  else:
    return False
```

And then use it inside a circuit:
```python
qc = QuantumCircuit(f.num_qubits)
...
qc.append(f.gate, f.qubits_list(0))
```

Or, you can define a function with parameters:
```python
@qlassf
def f(n: Int4, n_it: Param[int]) -> Int8:
  v = 0
  for x in range(n_it):
    v += n
  return n     
```

And then, you can bind it with a value:
```python
f4 = f.bind(n_it=4)
qc = QuantumCircuit(f4.num_qubits)
...
qc.append(f4.gate, f4.qubits_list(0))
```


## License

Read [LICENSE](LICENSE).