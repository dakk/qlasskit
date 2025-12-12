Qlasskit
====================================

.. image:: https://img.shields.io/badge/GitHub-Repository-blue?logo=github
   :alt: GitHub Repository
   :target: https://github.com/dakk/qlasskit
.. image:: https://img.shields.io/badge/supported_by-Unitary_Fund-ffff00.svg
   :alt: Unitary Fund
   :target: https://unitary.fund
.. image:: https://github.com/dakk/qlasskit/actions/workflows/ci.yaml/badge.svg
   :alt: CI Status
   :target: https://github.com/dakk/qlasskit/actions/workflows/ci.yaml
.. image:: https://img.shields.io/pypi/v/qlasskit
   :alt: PyPI - Version
   :target: https://pypi.org/project/qlasskit/
.. image:: https://img.shields.io/badge/license-Apache_2.0-blue
   :alt: License: Apache 2.0
   :target: https://opensource.org/licenses/Apache-2.0
.. image:: https://img.shields.io/badge/qlasskit-Discord-yellow?logo=discord&logoColor=f5f5f5
   :alt: Discord
   :target: https://discord.com/channels/764231928676089909/1210279373865754624
.. image:: https://app.codacy.com/project/badge/Grade/05acc06af76848028183a66448217d91
   :alt: Codacy Badge
   :target: https://app.codacy.com/gh/dakk/qlasskit/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade
.. image:: https://static.pepy.tech/badge/qlasskit
   :alt: Downloads
   :target: https://pepy.tech/project/qlasskit

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
   decompiler_and_optimizer.ipynb
   api
   cli_tools

.. toctree::
   :maxdepth: 2
   :caption: Examples

   example_grover.ipynb
   example_grover_sat.ipynb
   example_grover_subset.ipynb
   example_grover_hash.ipynb
   example_grover_sudoku.ipynb
   example_grover_factors.ipynb
   example_simon.ipynb
   example_deutsch_jozsa.ipynb
   example_bernstein_vazirani.ipynb
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