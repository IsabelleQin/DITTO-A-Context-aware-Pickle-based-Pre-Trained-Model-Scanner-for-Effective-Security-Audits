"""Create portable serialized representations of Python objects.

See module copyreg for a mechanism for registering custom picklers.
See module pickletools source for extensive comments.

Classes:

    Unpickler

Functions:

    load(file) -> object
    loads(bytes) -> object

Misc variables:

    __version__
    format_version
    compatible_formats

"""
import sys
import io
from emulation.opcodes import *
from emulation.actions import *
from components.helper import resetctr
import pickle
import logging
import _compat_pickle
# Callable implementation and representation
from collections.abc import Callable as callImp
from emulation.sensitive_state import Var as callRep
import time
from typing import final

__all__ = ["Unpickler", "load", "loads"]

logger = logging.getLogger("StaticUnpickler")
# Unpickling machinery
class StaticUnpickler(pickle._Unpickler):
    def load(self):
        """
        Reset the loading state
        """
        resetctr()
        # Enforce static persistent load
        self.persistent_load = self.static_persistent_load

        logger.warning(f"START - {time.asctime()} - New Pickle deserialization session starts")
        logger.warning("Statically generating operation trace...")
        result = None
        try:
            result = super().load()
            logger.warning(f"END - {time.asctime()} - Session ends; deserialization result: {result}")
            return result
        except Exception as e:
            logger.error(f"END - {time.asctime()} - Error parsing Pickle opcodes ({type(e)}): {e}")

    def static_persistent_load(self, pid):
        return pid

    def find_class(self, module, name):
        # Log the action first then try to get the real one
        # The real import is better for instantiate path check
        if self.proto < 3 and self.fix_imports:
            if (module, name) in _compat_pickle.NAME_MAPPING:
                module, name = _compat_pickle.NAME_MAPPING[(module, name)]
            elif module in _compat_pickle.IMPORT_MAPPING:
                module = _compat_pickle.IMPORT_MAPPING[module]
        callable = log_import(module, name)
        try: 
            act_callable = super().find_class(module, name)
            assert isinstance(act_callable, callImp)
            callable = act_callable
        except Exception as e: pass
        return callable

    # INST and OBJ differ only in how they get a class object.  It's not
    # only sensible to do the rest in a common routine, the two routines
    # previously diverged and grew different bugs.
    # klass is the class to instantiate, and k points to the topmost mark
    # object, following which are the arguments for klass.__init__.
    def _instantiate(self, klass, args):
        if (args or not isinstance(klass, type) or
            hasattr(klass, "__getinitargs__")):
            try:
                value = log_call(klass, args)
            except TypeError as err:
                raise TypeError("in constructor for %s: %s" %
                                (klass.__name__, str(err)), sys.exc_info()[2])
        else:
            value = log_new(klass, args)
        self.append(value)

    def load_newobj(self):
        args = self.stack.pop()
        cls = self.stack.pop()
        obj = log_new(cls, args)
        self.append(obj)
    pickle._Unpickler.dispatch[NEWOBJ[0]] = load_newobj

    def load_newobj_ex(self):
        kwargs = self.stack.pop()
        args = self.stack.pop()
        cls = self.stack.pop()
        obj = log_new(cls, args, kwargs)
        self.append(obj)
    pickle._Unpickler.dispatch[NEWOBJ_EX[0]] = load_newobj_ex

    # Prevent injection, do not fetch directly
    def get_extension(self, code):
        obj = log_extreg(code)
        self.append(obj)

    def load_reduce(self):
        args = self.stack.pop()
        func = self.stack[-1]
        self.stack[-1] = log_call(func, args)
    pickle._Unpickler.dispatch[REDUCE[0]] = load_reduce

    def load_append(self):
        value = self.stack.pop()
        list_obj = self.stack[-1]
        if isinstance(list_obj, (callImp, callRep)):
            ret = log_append(list_obj, [value])
            self.stack[-1] = ret
        else:
            list_obj.append(value)
    pickle._Unpickler.dispatch[APPEND[0]] = load_append

    def load_appends(self):
        items = self.pop_mark()
        list_obj = self.stack[-1]
        if isinstance(list_obj, (callImp, callRep)):
            ret = log_extend(list_obj, items)
            self.stack[-1] = ret
        else:
            try: extend = list_obj.extend
            except AttributeError: pass
            else:
                extend(items)
                return
            # Even if the PEP 307 requires extend() and append() methods,
            # fall back on append() if the object has no extend() method
            # for backward compatibility.
            for item in items:
                list_obj.append(item)
    pickle._Unpickler.dispatch[APPENDS[0]] = load_appends

    def load_setitem(self):
        value = self.stack.pop()
        key = self.stack.pop()
        dict_obj = self.stack[-1]
        if isinstance(dict_obj, (callImp, callRep)):
            ret = log_setitem(dict_obj, {key: value})
            self.stack[-1] = ret
        else:
            dict_obj[key] = value
    pickle._Unpickler.dispatch[SETITEM[0]] = load_setitem

    def load_setitems(self):
        items = self.pop_mark()
        dict_obj = self.stack[-1]
        if isinstance(dict_obj, (callImp, callRep)):
            vals = {}
            for i in range(0, len(items), 2): vals[items[i]] = items[i + 1]
            ret = log_setitem(dict_obj, vals)
            self.stack[-1] = ret
        else:
            for i in range(0, len(items), 2):
                dict_obj[items[i]] = items[i + 1]
    pickle._Unpickler.dispatch[SETITEMS[0]] = load_setitems

    def load_additems(self):
        items = self.pop_mark()
        set_obj = self.stack[-1]
        if isinstance(set_obj, (callImp, callRep)):
            ret = log_add(set_obj, items)
            self.stack[-1] = ret
        else:
            if isinstance(set_obj, set):
                set_obj.update(items)
            else:
                add = set_obj.add
                for item in items:
                    add(item)
    pickle._Unpickler.dispatch[ADDITEMS[0]] = load_additems

    def load_build(self):
        inst = self.stack[-2]
        if isinstance(inst, (callImp, callRep)):
            state = self.stack.pop()
            inst = self.stack.pop()
            ret = log_build(inst, state)
            self.stack.append(ret)
            return
        super().load_build()
    pickle._Unpickler.dispatch[BUILD[0]] = load_build


# Shorthands
def _load(file, *, fix_imports=True, encoding="ASCII", errors="strict",
          buffers=None):
    return StaticUnpickler(file, fix_imports=fix_imports, buffers=buffers,
        encoding=encoding, errors=errors).load()

def _loads(s, /, *, fix_imports=True, encoding="ASCII", errors="strict",
           buffers=None):
    if isinstance(s, str):
        raise TypeError("Can't load pickle from unicode string")
    file = io.BytesIO(s)
    return StaticUnpickler(file, fix_imports=fix_imports, buffers=buffers,
        encoding=encoding, errors=errors).load()

Unpickler = StaticUnpickler
load, loads =  _load, _loads