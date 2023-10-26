How it works
============

In order to translate python code to quantum circuit, qlasskit performs several transformations;
it starts from the python *AST* (abstract synthax tree) rewriting it to a simplified version. 
Then the simplified *AST* is translated to *boolean expressions* as intermediate
form. Then these boolean expressions are compiled into a *quantum circuit*.

While other existing libraries translate individual operations into quantum circuits and then 
combine them, qlasskit creates a single boolean expression for every output qubit of the entire 
function. This approach allows for further optimization using boolean properties.

For instance, let assume we have the following function:

.. code-block:: python

      def f_comp(b: bool, n: Qint2) -> Qint2:
            for i in range(3):
                  n += (1 if b else 2)
            return n

If we compile the whole function to a quantum circuit, we obtain the following quantum circuit:

.. code-block:: text

      q_0: ───░──────■────■────■────■────■────■────■─────────────────
              ░      │  ┌─┴─┐  │  ┌─┴─┐  │    │    │                 
      q_1: ───░──────■──┤ X ├──■──┤ X ├──■────┼────┼────■────────────
              ░      │  └───┘  │  └───┘  │    │    │    │            
      q_2: ───░──────┼─────────┼─────────┼────┼────┼────┼────■───────
              ░      │         │         │  ┌─┴─┐  │  ┌─┴─┐  │       
      q_3: ───░──────┼─────────┼─────────┼──┤ X ├──┼──┤ X ├──┼───────
              ░    ┌─┴─┐     ┌─┴─┐     ┌─┴─┐└───┘┌─┴─┐└───┘┌─┴─┐┌───┐
      q_4: ───░────┤ X ├─────┤ X ├─────┤ X ├─────┤ X ├─────┤ X ├┤ X ├
              ░    └───┘     └───┘     └───┘     └───┘     └───┘└───┘




While if we write three separate sums, compiling them separately, we obtain something like the 
following circuit:

.. code-block:: text

      q_0: ─░───■────■────■──────────────────░───■────■────■──────────────────░───■────■────■─────────────────
            ░   │    │    │                  ░   │    │    │                  ░   │    │    │                 
      q_1: ─░───■────┼────┼────■─────────────░───┼────┼────┼──────────────────░───┼────┼────┼─────────────────
            ░   │    │    │    │             ░   │    │    │                  ░   │    │    │                 
      q_2: ─░───┼────┼────┼────┼────■────────░───┼────┼────┼──────────────────░───┼────┼────┼─────────────────
            ░   │  ┌─┴─┐  │  ┌─┴─┐  │        ░   │    │    │                  ░   │    │    │                 
      q_3: ─░───┼──┤ X ├──┼──┤ X ├──┼────────░───■────┼────┼────■─────────────░───┼────┼────┼─────────────────
            ░ ┌─┴─┐└───┘┌─┴─┐└───┘┌─┴─┐┌───┐ ░   │    │    │    │             ░   │    │    │                 
      q_4: ─░─┤ X ├─────┤ X ├─────┤ X ├┤ X ├─░───┼────┼────┼────┼────■────────░───┼────┼────┼─────────────────
            ░ └───┘     └───┘     └───┘└───┘ ░   │  ┌─┴─┐  │  ┌─┴─┐  │        ░   │    │    │                 
      q_5: ─░────────────────────────────────░───┼──┤ X ├──┼──┤ X ├──┼────────░───■────┼────┼────■────────────
            ░                                ░ ┌─┴─┐└───┘┌─┴─┐└───┘┌─┴─┐┌───┐ ░   │    │    │    │            
      q_6: ─░────────────────────────────────░─┤ X ├─────┤ X ├─────┤ X ├┤ X ├─░───┼────┼────┼────┼────■───────
            ░                                ░ └───┘     └───┘     └───┘└───┘ ░   │  ┌─┴─┐  │  ┌─┴─┐  │       
      q_7: ─░────────────────────────────────░────────────────────────────────░───┼──┤ X ├──┼──┤ X ├──┼───────
            ░                                ░                                ░ ┌─┴─┐└───┘┌─┴─┐└───┘┌─┴─┐┌───┐
      q_8: ─░────────────────────────────────░────────────────────────────────░─┤ X ├─────┤ X ├─────┤ X ├┤ X ├
            ░                                ░                                ░ └───┘     └───┘     └───┘└───┘


As we can see from the circuit drawings, qlasskit approach needs half the number of qubits and approximately half the number of gates.


AST Traslator
-----------------
Given a python function, the `qlasskit.ast2logic` module walks its synthax tree translating all the statements / 
expressions to boolean expressions.


For instance, the following function:

.. code-block:: python

    def f(n: Qint4) -> bool:
        return n == 3

Is translated to this boolean expression:

.. code-block:: python

    _ret = n.0 & n.1 & ~n.2 & ~n.3


Compiler
------------
The boolean expressions are then being fed to the `qlasskit.compiler`` which translates boolean expressions
to invertible circuits, introducing auxiliary qubits. In this step, the compiler will automatically uncompute 
auxiliary qubits in order to reduce the number of qubits needed and the circuit footprint. 

For the compilation, two backends are supported:

- InternalCompiler
- Tweedledum.xag_synth


Result 
------

The result of the compiler is a quantum circuit represented with qlasskit `QCircuit`. This circuit
can now be exported to one of the supported framework.


The previous example function `f`, is translated to the following quantum circuit:


.. code-block:: text

       q_0: ─────────■─────────────────────────────────────■──────────
                     │                                     │          
       q_1: ─────────■─────────────────────────────────────■──────────
            ┌───┐    │             ┌───┐┌───┐              │     ┌───┐
       q_2: ┤ X ├────┼────────■────┤ X ├┤ X ├────■─────────┼─────┤ X ├
            ├───┤    │        │    └───┘├───┤    │         │     └───┘
       q_3: ┤ X ├────┼────────┼──────■──┤ X ├────┼─────────┼──────────
            └───┘    │        │    ┌─┴─┐└───┘    │         │          
       q_4: ─────────┼────────┼────┤ X ├─────────┼─────────┼──────────
                 ┌───┴───┐    │    └─┬─┘         │     ┌───┴────┐     
       q_5: ─────┤ Rx(π) ├────■──────┼───────────■─────┤ Rx(-π) ├─────
                 └───────┘┌───┴───┐  │       ┌───┴────┐└────────┘     
       q_6: ──────────────┤ Rx(π) ├──■───────┤ Rx(-π) ├───────────────
                          └───────┘          └────────┘               
