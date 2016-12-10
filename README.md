# AntLang4Python

An AntLang implementation in Python.

## Run REPL

> python3 antlang.py

## Python FFI

```antlang
log: (import python "math") dot "log"

print: (((eval python "globals()") dot "get")∘"__builtins__") dot "print"

print∘"Hello World!"
```
