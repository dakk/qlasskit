Supported python subset
====================================

Qlasskit supports a subset of python. This subset will be expanded, but it is
limited by the linearity of quantum circuits and by the number of qubits.

The structure of a qlasskit function has the following pattern:

.. code-block:: python

   @qlasskit
   def f(param: type, [...param: type]) -> type:
      statement
      ...
      statement


Types
-----

All types has a static size. 

bool
^^^^

Boolean type.


Qint
^^^^

Unsigned integers; `Qint[2]` has 2 bits, and there other sizes are supported.
Single bit of the Qint are accessible by the subscript operator `[]`.
All the supported sizes have a constructor `Qintn()` defined in `qlasskit.types`.

Qfixed
^^^^^^

Fixed point rational number; `Qfixed[2,3]` has 2 bits for the integer part and 3 bits for the fractional.
All the supported sizes have a constructor `Qfixedn_m()` defined in `qlasskit.types`.

Qchar
^^^^^

A character.

Tuple
^^^^^

Container type holding different types.


List
^^^^

Qlist[T, size] denotes a fixed-size list in qlasskit. 
For example, the list `[1,2,3]` is typed as `Qlist[Qint[2],3]`.


Matrix
^^^^^^

Qmatrix[T, m, n] denotes a fixed-size list in qlasskit. 
For example, the matrix `[[1,2],[3,4]]` is typed as `Qmatrix[Qint[2],2,2]`.





Expressions
-----------

Constants
^^^^^^^^^^^^^

.. code-block:: python

   True

.. code-block:: python

   42

.. code-block:: python

   3.14

.. code-block:: python

   'a'
   

Tuple
^^^^^

.. code-block:: python

   (a, b)

List (fixed size)
^^^^^^^^^^^^^^^^^

.. code-block:: python
   
   [a, b]


2D Matrix (fixed size)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   
   [[a, b], [c,d]]


Subscript
^^^^^^^^^

.. code-block:: python

   a[0]

Boolean operators
^^^^^^^^^^^^^^^^^

.. code-block:: python

   not a

.. code-block:: python

   a and b

.. code-block:: python

   a or b 



If expressions
^^^^^^^^^^^^^^

.. code-block:: python

   a if b else c

Comparators
^^^^^^^^^^^

.. code-block:: python

   a > b or b <= c and c == d or c != a


Unary Op
^^^^^^^^^

.. code-block:: python

   ~a



Bin Op
^^^^^^^^^

.. code-block:: python

   a << 1

.. code-block:: python

   a >> 2

.. code-block:: python

   a + b

.. code-block:: python

   a - b

.. code-block:: python

   a * b

.. code-block:: python

   a ** b

.. code-block:: python

   a % 2

.. note::
   Modulo operator only works with 2^n values.
   

Function call
^^^^^^^^^^^^^

Bultin functions:

* `print()`: debug function, ignore by conversion
* `len(Tuple)`, `len(Qlist)``: returns the length of a tuple
* `max(a, b, ...)`, `max(Tuple)`, `max(Qlist)`: returns the max of a tuple
* `min(a, b, ...)`, `min(Tuple)`, `min(Qlist)`: returns the min of a tuple
* `sum(Tuple)`, `sum(Qlist)`: returns the sum of the elemnts of a tuple / list
* `all(Tuple)`, `all(Qlist)`: returns True if all of the elemnts are True
* `any(Tuple)`, `any(Qlist)`: returns True if any of the elemnts are True
* `ord(Qchar)`: returns the integer value of the given Qchar
* `chr(Qint)`: returns the char given its ascii code
* `int(Qfixed | Qint)`: returns the integer part of a Qfixed 
* `float(Qint | Qfixed)`: returns a Qfixed representing the Qint


Statements 
----------

Assign
^^^^^^

.. code-block:: python

   c = not a

Return
^^^^^^

.. code-block:: python

   return b+1


For loop
^^^^^^^^

.. code-block:: python

   for i in range(4):
      a += i


.. note::
   Please note that in qlasskit, for loops are unrolled during compilation. Therefore, 
   it is essential that the number of iterations for each for loop is known at the 
   time of compilation.

Function def
^^^^^^^^^^^^

.. code-block:: python

   def f(t: Qlist[Qint[4],2]) -> Qint[4]:
      return t[0] + t[1]


If then else
^^^^^^^^^^^^

.. code-block:: python

   c = 0
   if cond:
      c += 12
   else:
      c += 13

.. note::
   At present, the if-then-else statement in qlasskit is designed to support branch bodies 
   that exclusively contain assignment statements.



Quantum Hybrid
---------------

In a qlassf function, you have the option to utilize quantum gates through the Q module. It's 
important to keep in mind that incorporating quantum gates within a qlasskit function leads 
to a Python function that exhibits distinct behaviors compared to its quantum counterpart.

.. code-block:: python

   def bell(a: bool, b: bool) -> bool:
      return Q.CX(Q.H(a), b)

