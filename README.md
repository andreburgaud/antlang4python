# AntLang4Python

An AntLang implementation in Python.

## Run REPL

> python3 antlang.py

## Make Build

### Install cx\_Freeze

> pip3 install cx\_Freeze

### Build Executable

> python3 build.py

### Tests

Unit tests are using `pytest` (http://doc.pytest.org/en/latest/), therefore `pytest` needs to be
installed.

#### Install pytest

To isolate external Python dependencies to this project only, it is recommended to use a Python
virtual environment.

For the first installation:

```
$ python3 -m venv ENV
$ . ENV/bin/activate
$ pip install -r requirements.txt
```

#### Test Execution

```
$ . ENV/bin/activate
$ pytest
================================== test session starts =============================================
platform darwin -- Python 3.6.0rc1, pytest-3.0.5, py-1.4.31, pluggy-0.4.0
rootdir: /Users/andre/AB/git/antlang4python, inifile:
collected 57 items

test_ant.py .........................................................
================================== 57 passed in 0.15 seconds =======================================
```

To execute the tests with verbosity, use the option `-v` or `--verbose`:
```
$ pytest -v
```

To deactivate the Python virtual environment:

```
$ deactivate
```
