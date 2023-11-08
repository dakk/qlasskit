from setuptools import setup

import qlasskit

setup(
    name="qlasskit",
    version=qlasskit.__version__,
    python_requires=">= 3.8.2",
    description="",
    author="Davide Gessa",
    setup_requires="setuptools",
    author_email="gessadavide@gmail.com",
    packages=[
        "qlasskit",
        "qlasskit.boolopt",
        "qlasskit.types",
        "qlasskit.ast2logic",
        "qlasskit.qcircuit",
        "qlasskit.compiler",
        "qlasskit.algorithms",
    ],
    zip_safe=False,
    install_requires=["sympy==1.12"],
    extras_require={
        "tweedledum": ["tweedledum==1.1.1"],
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
