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

Unsigned integers; this type has subtypes for different Qint sizes (Qint2, Qint4, Qint8, Qint12, Qint16). 
Single bit of the Qint are accessible by the subscript operator `[]`.


Tuple
^^^^^

Container type holding different types.


List
^^^^

A fixed size list; its type is `Qlist[T, size]`.


Expressions
-----------

Constants
^^^^^^^^^^^^^

.. code-block:: python

   True

.. code-block:: python

   42


Tuple
^^^^^

.. code-block:: python

   (a, b)

List (fixed size)
^^^^^^^^^^^^^^^^^

.. code-block:: python
   [a, b]


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

   a > b or b <= c


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

   

Function call
^^^^^^^^^^^^^

Bultin functions:
- `print()`: debug function, ignore by conversion
- `len(Tuple)`, `len(Qlist)``: returns the length of a tuple
- `max(a, b, ...)`, `max(Tuple)`, `max(Qlist)`: returns the max of a tuple
- `min(a, b, ...)`, `min(Tuple)`, `min(Qlist)`: returns the min of a tuple
- `sum(Tuple)`, `sum(Qlist)`: returns the sum of the elemnts of a tuple / list
- `all(Tuple)`, `all(Qlist)`: returns True if all of the elemnts are True
- `any(Tuple)`, `any(Qlist)`: returns True if any of the elemnts are True



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



Function def
^^^^^^^^^^^^

.. code-block:: python

   def f(t: Qlist[Qint4,2]) -> Qint4:
      return t[0] + t[1]


If then else
^^^^^^^^^^^^

.. code-block:: python

   c = 0
   if cond:
      c += 12
   else:
      c += 13
