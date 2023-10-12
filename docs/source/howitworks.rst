How it works
============

In order to translate python code to quantum circuit, qlasskit performs several transformations;
it starts from the python *AST* (abstract synthax tree) creating *boolean expressions* as intermediate
form. Then these boolean expressions are compiled into a *quantum circuit*.

While other existing libraries translate individual operations into quantum circuits and then 
combine them, qlasskit creates a single boolean expression for every output qubit of the entire 
function. This approach allows for further optimization using boolean properties.

For instance, let assume we have the following function:

.. code-block:: python

    def f_comp(n: Qint4) -> bool:
        return n > 3 or n == 7

If we compile the whole function to a quantum circuit, we obtain the following circuit, created by
this boolean expression `n.2 | n.3 | (n.0 & n.1 & n.2 & ~n.3)`:

.. code-block:: text

        f_comp                                    
    q_0: ───░─────────────────────■─────────────────
            ░                     │                 
    q_1: ───░─────────────────────■─────────────────
            ░                     │                 
    q_2: ───░──────■──────────────■─────────────────
            ░      │              │                 
    q_3: ───░──────┼────■─────────┼─────────────────
            ░    ┌─┴─┐  │  ┌───┐  │                 
    q_4: ───░────┤ X ├──┼──┤ X ├──┼─────────■───────
            ░    └───┘┌─┴─┐├───┤  │         │       
    q_5: ───░─────────┤ X ├┤ X ├──■─────────■───────
            ░         └───┘└───┘┌─┴─┐┌───┐  │       
    q_6: ───░───────────────────┤ X ├┤ X ├──■───────
            ░                   └───┘└───┘┌─┴─┐┌───┐
    q_7: ───░─────────────────────────────┤ X ├┤ X ├
            ░                             └───┘└───┘


While if we decompose the function in 3 operations `n==7`, `n>3`, `a and b`, we obtain something like 
the following circuit (qubit uncomputing is disabled to show the real number of gates):

.. code-block:: text

           =                 >                           |                          
    q_0:  ─░─────────────■───░───────────────────────────░──────────────────────────
           ░             │   ░                           ░                          
    q_1:  ─░─────────────■───░───────────────────────────░──────────────────────────
           ░             │   ░                           ░                          
    q_2:  ─░─────────────■───░───■───────────────────────░──────────────────────────
           ░             │   ░   │                       ░                          
    q_3:  ─░───■─────────┼───░───┼────■──────────────────░──────────────────────────
           ░ ┌─┴─┐┌───┐  │   ░   │    │                  ░                          
    q_4:  ─░─┤ X ├┤ X ├──■───░───┼────┼──────────────────░──────────────────────────
           ░ └───┘└───┘┌─┴─┐ ░   │    │                  ░                          
    q_5:  ─░───────────┤ X ├─░───┼────┼──────────────────░───■──────────────────────
           ░           └───┘ ░   │    │                  ░   │                      
    q_6:  ─░─────────────────░───┼────┼──────────────────░───┼──────────────────────
           ░                 ░ ┌─┴─┐  │  ┌───┐           ░   │                      
    q_7:  ─░─────────────────░─┤ X ├──┼──┤ X ├──■────────░───┼──────────────────────
           ░                 ░ └───┘┌─┴─┐├───┤  │        ░   │                      
    q_8:  ─░─────────────────░──────┤ X ├┤ X ├──■────────░───┼──────────────────────
           ░                 ░      └───┘└───┘┌─┴─┐┌───┐ ░   │                      
    q_9:  ─░─────────────────░────────────────┤ X ├┤ X ├─░───┼────■─────────────────
           ░                 ░                └───┘└───┘ ░ ┌─┴─┐  │  ┌───┐          
    q_10: ─░─────────────────░───────────────────────────░─┤ X ├──┼──┤ X ├──■───────
           ░                 ░                           ░ └───┘┌─┴─┐├───┤  │       
    q_11: ─░─────────────────░───────────────────────────░──────┤ X ├┤ X ├──■───────
           ░                 ░                           ░      └───┘└───┘┌─┴─┐┌───┐
    q_12: ─░─────────────────░───────────────────────────░────────────────┤ X ├┤ X ├
           ░                 ░                           ░                └───┘└───┘



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




Result 
------

The result of the compiler is a quantum circuit represented with qlasskit `QCircuit`. This circuit
can now be exported to one of the supported framework.


The previous example function `f`, is translated to the following quantum circuit:


.. code-block:: text

    q_0: ─────────────────■──
                          │  
    q_1: ─────────────────■──
                          │  
    q_2: ──■──────────────┼──
           │              │  
    q_3: ──┼────■─────────┼──
         ┌─┴─┐  │  ┌───┐  │  
    q_4: ┤ X ├──┼──┤ X ├──■──
         └───┘┌─┴─┐├───┤  │  
    q_5: ─────┤ X ├┤ X ├──■──
              └───┘└───┘┌─┴─┐
    q_6: ───────────────┤ X ├
                        └───┘
