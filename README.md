# Qlasskit

[![Unitary Fund](https://img.shields.io/badge/supported_by-Unitary_Fund-ffff00.svg)](https://unitary.fund)
![CI Status](https://github.com/dakk/qlasskit/actions/workflows/ci.yaml/badge.svg)
![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue)


Qlasskit is a Python library that allows quantum developers to write classical algorithms in pure Python and translate them into unitary operators (gates) for use in quantum circuits, using boolean expressions as intermediate form.

This tool will be useful for any algorithm that relies on a 'blackbox' function and for describing the classical components of a quantum algorithm.



```python
@qlassf
def hash(k: Qint4) -> bool:
    h = True
    for i in range(4):
        h = h and k[i]
    return h
```

Qlasskit will take care of translating the function to boolean expressions, simplify them and
translate to a quantum circuit.

![Groover](docs/source/_images/hash_circ.png)

Then, we can use groover to find which hash(k) returns True:

```python
from qlasskit.algorithms import Groover

algo = Groover(hash, True)
qc = algo.circuit().export("circuit", "qiskit")
```

And that's it:

![Groover](docs/source/_images/groover_circ.png)


You can also define a function with parameters:
```python
@qlassf
def f(n: Qint4, n_it: Param[int]) -> Qint8:
  v = 0
  for x in range(n_it):
    v += n
  return n     
```

And then, you can bind it with a value:
```python
f4 = f.bind(n_it=4)
```

Use other functions:

```python
@qlassf
def equal_8(n: Qint4) -> bool:
  return equal_8

@qlassf
def f(n: Qint4) -> bool:
  n = n+1 if equal_8(n) else n
  return n
```

Qlasskit supports complex data types, like tuples and fixed size lists:

```python
@qlassf
def f(a: Tuple[Qint8, Qint8]) -> Tuple[bool, bool]:
  return a[0] == 42, a[1] == 0
```

```python
@qlassf
def search(alist: List4[Qint2], to_search: Qint2):
  for x in alist:
    if x == to_search:
      return True
  return False
```


## Roadmap

Read [TODO](TODO.md) for details about the roadmap and TODOs.

## Contributing

Read [CONTRIBUTING](CONTRIBUTING.md) for details.

## License

This software is licensed with [Apache License 2.0](LICENSE).


## Cite

```
@software{qlasskit2023,
  author = {Davide Gessa},
  title = {qlasskit: a python-to-quantum circuit compiler},
  url = {https://github.com/dakk/qlasskit},
  year = {2023},
}
```

## About the author

Davide Gessa (dakk)
- https://twitter.com/dagide
- https://dakk.github.io/
- https://medium.com/@dakk