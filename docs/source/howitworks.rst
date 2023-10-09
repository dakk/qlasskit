How it works
============

In order to translate python code to quantum circuit, qlasskit performs several transformations;
it starts from the python *AST* (abstract synthax tree) creating *boolean expressions* as intermediate
form. Then these boolean expressions are compiled into a *quantum circuit*.


AST Traslator
-----------------
Given a python function, the `qlasskit.ast2logic` module walks its synthax tree translating all the statements / 
expressions to boolean expressions.


Compiler
------------
The boolean expressions are then being fed to the `qlasskit.compiler`` which translates boolean expressions
to invertible circuits, introducing auxiliary qubits. In this step, the compiler will automatically uncompute 
auxiliary qubits in order to reduce the number of qubits needed and the circuit footprint. 


Result 
------

The result of the compiler is a quantum circuit represented with qlasskit `QCircuit`. This circuit
can now be exported to one of the supported framework.
