import torch
__all__ = [
    "resetctr", "getctr", "addctr", 
    "resetquery", "setquery", "getquery", "SAFE_GLOBALS",
    "resetrisky", "addrisky", "getrisky", "isrisky"
    ]

SAFE_GLOBALS = frozenset(torch._weights_only_unpickler._get_allowed_globals().keys())

# Variable counter
ctr = 0
def resetctr(): global ctr; ctr = 0
def getctr(): global ctr; return ctr
def addctr(): global ctr; ctr += 1

# Whether the model needs to be checked with LLM query
QUERY = False
def resetquery(): global QUERY; QUERY = False
def setquery(): global QUERY; QUERY = True
def getquery(): global QUERY; return QUERY

# Risky targets identified in the session
risky_globals = set()
def resetrisky(): global risky_globals; risky_globals = set()
def addrisky(target): global risky_globals; risky_globals.add(target)
def getrisky(): global risky_globals; return risky_globals
def isrisky(target): global risky_globals; return target in risky_globals