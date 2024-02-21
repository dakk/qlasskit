Qlasskit
====================================

Qlasskit is a Python library that allows quantum developers to write classical algorithms in pure 
Python and translate them into unitary operators (gates) for use in quantum circuits supporting a wide 
range of quantum frameworks.

Qlasskit also support exporting to Binary Quadratic Models (bqm, ising and qubo) ready to be used in
quantum annealers, ising machines, simulators, etc.

.. toctree::
   :maxdepth: 2
   :caption: Qlasskit

   quickstart.ipynb   
   how_it_works.ipynb
   supported
   parameters.ipynb
   algorithms.ipynb
   exporter.ipynb
   bqm.ipynb
   api

.. toctree::
   :maxdepth: 2
   :caption: Examples

   example_grover.ipynb
   example_grover_subset.ipynb
   example_grover_hash.ipynb
   example_grover_sudoku.ipynb
   example_grover_factorize.ipynb
   example_simon.ipynb
   example_deutsch_jozsa.ipynb
   example_unitary_of_f.ipynb
   example_big_circuit.ipynb
   example_bqm_tsp.ipynb


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Cite
======

.. code-block:: latex

   @software{qlasskit2023,
     author = {Davide Gessa},
     title = {qlasskit: a python-to-quantum circuit compiler},
     url = {https://github.com/dakk/qlasskit},
     year = {2023},
   }