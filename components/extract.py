from components.helper import SAFE_GLOBALS
import json

__all__ = ["extract"]

def extract(log_path, extract_path):
    safe = {i for i in SAFE_GLOBALS}
    sessions = []
    lines = []
    with open(log_path, "r") as f:
        lines = [l.strip() for l in f.readlines()]

    # Separate risky and safe operations
    for line in lines:
        # Start a new session
        if line.startswith("START"):
            session = {"remain": [], "compressed": []}
        elif line.startswith("END"):
            sessions.append(session)
        elif line.startswith("{") and line.endswith("}"):
            attr = json.loads(line)
            target = attr["assign_with"]
            # Should only have one remaining
            for action in [".__call__", ".__new__", ".__setstate__", ".__append__", ".__extend__", ".__add__"]:
                target = target.split(action)[0]
            
            if target in tuple(safe):
                session["compressed"].append(attr["id"])
                safe.add(attr["id"])
            else:
                session["remain"].append(attr)

    with open(extract_path, "w") as f:
        for i, session in enumerate(sessions):
            f.write(f"Session-{i} STARTS\n")
            f.write("Critical construction process:\n")
            for item in session["remain"]:
                formatted = item
                f.write(f"{formatted}\n")
            f.write(f"Session-{i} ENDS\n")