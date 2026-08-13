import logging
import pickle
import emulation.static_pickle as modeling
from pathlib import Path
from components.helper import resetquery, resetrisky
import torch
import os
from nemo.core.connectors.save_restore_connector import SaveRestoreConnector
from nemo.utils.app_state import AppState
from contextlib import nullcontext
import tempfile
import joblib.numpy_pickle as jnp
import _pickle
__all__ = ["hook", "ConnectorWrapper"]

def hook_pickle():
    # Hook Pickle
    pickle._Unpickler = modeling.StaticUnpickler
    pickle.Unpickler = modeling.StaticUnpickler
    pickle._load, pickle._loads = modeling._load, modeling._loads
    pickle.load, pickle.loads = modeling._load, modeling._loads
    
    jnp.Unpickler = modeling.StaticUnpickler
    jnp.NumpyUnpickler.__bases__ = (modeling.StaticUnpickler,)  # if needed
    
    _pickle.Unpickler = modeling.StaticUnpickler
    

def hook_torch():
    # Hook PyTorch
    org_torch_load = torch.load
    def patched_torch_load(f, map_location=None, pickle_module=pickle, **kwargs):
        # Enforce
        if 'weights_only' in kwargs: kwargs['weights_only'] = False
        return org_torch_load(f, map_location=map_location, pickle_module=pickle_module, **kwargs)
    torch.load = patched_torch_load

# Hook NeMo override the state dict loading
class ConnectorWrapper(SaveRestoreConnector):
    def load_config_and_state_dict(
            self,
            restore_path: str,
            map_location = torch.device('cpu'),
            return_config: bool = False,
        ):
        # Get path where the command is executed - the artifacts will be "retrieved" there
        # (original .nemo behavior)
        cwd = os.getcwd()
        app_state = AppState()
        # Determine if we should use a pre-extracted directory
        use_extracted_dir = self.model_extracted_dir is not None and os.path.isdir(self.model_extracted_dir)

        if use_extracted_dir:
            logging.info(f"Restoration will occur within pre-extracted directory : " f"`{self.model_extracted_dir}`.")
        # Use nullcontext if we have an extracted dir, otherwise create a temp directory
        dir_context = nullcontext(self.model_extracted_dir) if use_extracted_dir else tempfile.TemporaryDirectory()

        with dir_context as tmpdir:
            try:
                if not use_extracted_dir:
                    # Extract the nemo file into the temporary directory
                    filter_fn = None
                    if return_config:
                        filter_fn = lambda name: '.yaml' in name
                    members = self._filtered_tar_info(restore_path, filter_fn=filter_fn)
                    self._unpack_nemo_file(path2file=restore_path, out_folder=tmpdir, members=members)
                    
                # Change current working directory to
                os.chdir(tmpdir)
                if app_state.model_parallel_size is not None and app_state.model_parallel_size > 1:
                    model_weights = self._inject_model_parallel_rank_for_ckpt(tmpdir, self.model_weights_ckpt)
                else:
                    model_weights = os.path.join(tmpdir, self.model_weights_ckpt)
                os.chdir(cwd)
                # add load_state_dict override
                if app_state.model_parallel_size is not None and app_state.model_parallel_size > 1:
                    model_weights = self._inject_model_parallel_rank_for_ckpt(tmpdir, self.model_weights_ckpt)
                state_dict = self._load_state_dict_from_disk(model_weights, map_location=map_location)
            finally:
                os.chdir(cwd)
        return 


def hook():
    # Reset the query and delete the old log
    hook_pickle()
    hook_torch()