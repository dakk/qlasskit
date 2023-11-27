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
pip install sphinx sphinx_rtd_theme sphinx_rtd_dark_mode myst_nb
cd docs
make html
```