# Contributing

## Prepare the env

```
pyenv virtualenv qlasskit-env
pip install tox
```


## Pre-commit checks

```
tox
```


## Make docs

```
pip install sphinx sphinx_rtd_theme myst_parser
cd docs
make html
```