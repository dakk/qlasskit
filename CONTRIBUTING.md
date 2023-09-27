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
pip install sphinx
cd docs
make html
```