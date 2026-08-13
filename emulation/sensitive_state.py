from components.helper import getctr, addctr, setquery, addrisky, SAFE_GLOBALS
from torch.storage import TypedStorage
from torch import typename

__all__ = ["Var"]

# Vars
class Var:
    def __init__(self, target, action, args=None, keywords=None):
        # Compose the action
        if action == "import":
            self.action = f"import {target[0]} from {target[1]}"
            # Verify with the allowlist
            glob = f"{target[0]}.{target[1]}"
            self.id = glob
            if glob not in SAFE_GLOBALS: 
                addrisky(glob)
                setquery()
        elif action == "ext_import":
            self.action = "pickle._Unpickler.get_extension"
            # Directly add because of potential injection
            self.id = f"pickle._Unpickler.get_extension(code={args[0]})"
            addrisky(self.id)
            setquery()
        else:
            addctr()
            # No security check for other actions
            if isinstance(target, Var): glob = target.id
            else: glob = f"{target.__module__}.{target.__name__}"
            self.id = f"Var{getctr()}"
            self.action = f"{glob}.{action}"

        # Abstract argument tuples and dictionaries
        if args:
            self.args = []
            for arg in args:
                if isinstance(arg, Var): self.args.append(arg.id)
                elif isinstance(arg, TypedStorage): 
                    # PyTorch abstraction, storages are safe
                    self.args.append(f'[{typename(arg)}(device={arg.device}) of size {len(arg)}]')
                else: self.args.append(arg)
        else: self.args = []

        if keywords:
            self.keywords = {}
            for k, v in keywords.items():
                if isinstance(v, Var): self.keywords[k] = v.id
                elif isinstance(v, TypedStorage): 
                    self.keywords[k] = f'[{typename(v)}(device={v.device}) of size {len(v)}]'
                else: self.keywords[k] = v
        else: self.keywords = {}
            
    def __repr__(self):
        return self.id
    
    def log(self):
        if not self.args and not self.keywords:
            assign_with = f"{self.action}()"
        elif self.args and not self.keywords:
            assign_with = f"{self.action}(*args={tuple(self.args)})"
        elif not self.args and self.keywords:
            assign_with = f"{self.action}(**kwargs={self.keywords})"
        else:
            assign_with = f"{self.action}(*args={tuple(self.args)},**kwargs={self.keywords})"
        
        log_dict = {
            "id": self.id, 
            "assign_with": assign_with
        }
        # Remove empty entries
        return log_dict