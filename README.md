# Qlasskit

[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](https://unitary.fund)
![CI Status](https://github.com/dakk/qlasskit/actions/workflows/ci.yaml/badge.svg)


Qlasskit is a Python library that allows quantum developers to write classical algorithms in pure Python and translate them into unitary operators (gates) for use in quantum circuits.

This tool will be useful for any algorithm that relies on a 'blackbox' function and for describing the classical components of a quantum algorithm.



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

Qlasskit (will) supports complex data types, like tuples and fixed size lists:

```python
@qlassf
def f(a: Tuple[Int8, Int8]) -> Tuple[bool, bool]:
  return a[0] == 42, a[1] == 0
```

```python
@qlassf
def search(alist: List4[Int2], to_search: Int2):
  for x in alist:
    if x == to_search:
      return True
  return False
```


## License

Read [LICENSE](LICENSE).