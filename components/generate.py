import logging
import pickle
import emulation.static_pickle as static_pickle
from pathlib import Path
from components.helper import resetquery, resetrisky
from components.hook import *
import torch
import dill
import joblib

__all__ = ["scan"]
logger = logging.getLogger(f"StaticUnpickler")
logger.setLevel(logging.INFO)
logger.propagate = False
EXTENSION = {
    "Pickle": [".pickle"],
    "Dill": [".dill"],
    "PyTorch": [".pkl", ".pt", ".pth", ".ckpt", ".bin", ".zip", ".tar"],
    "Joblib": [".joblib"],
    "NeMo": [".nemo"],
    "NumPy": [".npz", ".npy"]
}

def set_handler(logger, path, mode, formatter="%(asctime)s - %(name)s - %(levelname)s - %(message)s"):
    handler = logging.FileHandler(path, mode=mode)
    handler.setFormatter(logging.Formatter(formatter))
    # Handler swap, redirect the stream
    for h in logger.handlers[:]:
        if isinstance(h, logging.FileHandler):
            h.close()
            logger.removeHandler(h)
    logger.addHandler(handler)

def scan(model_path, log_path="full_trace.log", mode=None):
    # Reset the query and delete the old log
    resetquery()
    resetrisky()
    Path(log_path).unlink(missing_ok=True)
    Path(log_path).parent.mkdir(exist_ok=True, parents=True)
    # Configure the logger
    set_handler(logger, log_path, "a", "%(message)s")
    
    # Infer loading module based on suffix
    if not mode:
        suffix = Path(model_path).suffix
        if suffix in EXTENSION["Pickle"]: mode = "Pickle"
        elif suffix in EXTENSION["Dill"]: mode = "Dill"
        elif suffix in EXTENSION["Joblib"]: mode = "Joblib"
        elif suffix in EXTENSION["PyTorch"]: mode = "PyTorch"
        elif suffix in EXTENSION["NeMo"]: mode = "NeMo"
        elif suffix in EXTENSION["NumPy"]: mode = "NumPy"
        else: raise ValueError(f"Unknown format: {suffix}! Please specify loading mode.")

    # Check extension
    try:
        match mode:
            case "Pickle":
                with open(model_path, "rb") as f: pickle.load(f)
            case "Dill":
                with open(model_path, "rb") as f: dill.load(f)
            case "Joblib":
                joblib.load(model_path)
            case "PyTorch":
                torch.load(model_path, map_location=torch.device('cpu'))
            case "NeMo":
                ConnectorWrapper().load_config_and_state_dict(model_path)
            case "NumPy":
                import numpy as np
                with open(model_path, "rb") as f:
                    data = np.load(f, allow_pickle=True)
                    # For .npz files, we must force it to read an array to trigger the check
                    if suffix == ".npz":
                        for key in data.files:
                            _ = data[key]
            case _:
                raise ValueError(f"Unknown loading mode: {mode}!")
    except Exception as e:
        logger.error(f"Error deserializing {model_path} ({type(e)}): {e}")