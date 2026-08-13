from emulation.sensitive_state import Var
import logging
import pickle
from pathlib import Path
import json
logger = logging.getLogger("StaticUnpickler")

__all__ = [
    "log_extreg", "log_import",
    "log_call", "log_new", "log_build", 
    "log_setitem", "log_append", "log_extend", "log_add", 
    ]

def register(callable):
    logger.info(json.dumps(callable.log()))
    return callable
    
def log_call(callable, args):
    return register(Var(callable, "__call__", args))

def log_new(callable, args, keywords=None):
    return register(Var(callable, "__new__", args, keywords))
    
def log_build(callable, args):
    return register(Var(callable, "__setstate__", args))

def log_setitem(callable, keywords):
    return register(Var(callable, "__setitem__", keywords=keywords))

def log_append(callable, args):
    return register(Var(callable, "__append__", args))

def log_extend(callable, args):
    return register(Var(callable, "__extend__", args))

def log_add(callable, args):
    return register(Var(callable, "__add__", args))

def log_extreg(code):
    # return register(Var(pickle._Unpickler.get_extension, "ext_import", [code]))
    return Var(pickle._Unpickler.get_extension, "ext_import", [code])

def log_import(module, name):
    # return register(Var((module, name), "import"))
    return Var((module, name), "import")