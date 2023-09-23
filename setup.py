from setuptools import find_packages, setup

import qlasskit

setup(
    name="qlasskit",
    version=qlasskit.__version__,
    description="",
    author="Davide Gessa",
    setup_requires="setuptools",
    author_email="gessadavide@gmail.com",
    packages=[
        "qlasskit",
    ],
    entry_points={
        "console_scripts": [],
    },
    zip_safe=False,
    install_requires=["sympy==1.12"],
)
