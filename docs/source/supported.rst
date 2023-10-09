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