# Contributing

## Prepare the env

```
pyenv virtualenv 3.8.16 qlasskit-env
pip install tox
```


## Pre-commit checks

```
tox
```


## Make docs

```
pip install sphinx sphinx_rtd_theme
cd docs
make html
```