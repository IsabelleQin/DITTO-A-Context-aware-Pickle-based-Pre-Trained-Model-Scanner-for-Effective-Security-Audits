# !!! Do not run this directly on your PC, use docker !!!
from tqdm import tqdm
import json
from pathlib import Path
from huggingface_hub import hf_hub_download
import os
import torch
import numpy as np
import tarfile
import shutil
import pandas as pd
import requests
import time
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_XET_NUM_CONCURRENT_RANGE_GETS"] = "1"
HF_KEY = "YOUR_HF_KEY"
INPUT = "./hf_investigation/repos/all_repo.json"
OUTPUT = "./hf_investigation/repos/has_pickle.csv"
ROOT = "./hf_investigation/repos/downloads"

# Skip some files to speed up the scanning
CHECK = {
    ".pkl", ".pickle", ".dill", ".joblib", 
    ".pth", ".pt", ".ckpt", ".bin", ".tar", ".zip", 
    ".npz", ".npy", ".nemo"
}
# No need to check for now
STRONG = {".pkl", ".pickle", ".dill", ".joblib"}
TO_LOAD = {".pth", ".pt", ".ckpt", ".bin", ".tar", ".zip"}

suffix = set()
with open(INPUT, "r") as f:
    repos = json.load(f)
    
def has_files(dir):
    path = Path(dir)
    return any(item.is_file() for item in path.iterdir())

def scan_hf(repo_id, file):
    # Check Pickle status, retry until succeed
    while True:
        try:
            # Check all paths in a repo
            result = requests.post(
                f"https://huggingface.co/api/models/{repo_id}/paths-info/main",
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {HF_KEY}"},
                json = {"paths": [file], "expand": True}
            )
            if result.status_code == 200:
                result = result.json()
                status = result[0]["securityFileStatus"]["pickleImportScan"]["status"]
                # Sleep 1s to avoid processing too fast
                time.sleep(1)
                return status
            else:
                # Check whether is not on the authorized list, check manually
                if "not in the authorized list" in result.text: 
                    print(f"No access error: {result.text}, set safety status to unknown")
                    return "unknown"
                print(f"Error {result.status_code} occurred ({result.text})! Retry after 1 second...")
                time.sleep(1)
        except Exception as e: 
            # Refresh if it is just "securityFileStatus":
            if not "securityFileStatus" in e:
                # Check manually
                print(f"An error {e} occurred! Safety status unknown...")
                return "unknown"
            else: time.sleep(0.1)

for i, repo in enumerate(tqdm(repos)):
    siblings = [s for s in repo["siblings"] if Path(s).suffix in CHECK]
    for file in siblings:
        isPickle = True
        status = scan_hf(repo['id'], file)
        if not status in ("unscanned", "error", "unknown"):
            with open(OUTPUT, "a") as f: 
                f.write(f"{repo['id']},{file},True,{status}\n")
            continue
        
        target = f"{ROOT}/{repo['id']}/{file}"
        path = f"{ROOT}/{repo['id']}"
        
        # Download if not exist
        if target.endswith(".nemo"):
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                Path(target).unlink(missing_ok=True)
                dir = hf_hub_download(repo["id"], file, local_dir=path)
            except Exception as e:
                with open(OUTPUT, "a") as f: 
                    f.write(f"{repo['id']},{file},unk,unk\n")
                print(f"{repo['id']}/{file} download failed due to {e}")
                continue
            
        # Case 1: Strong indicator
        if Path(file).suffix in STRONG: pass
        
        # Case 2: Load with torch
        elif Path(file).suffix in TO_LOAD:
            try:
                torch.load(target, map_location=torch.device('cpu'), weights_only=False)
            except ModuleNotFoundError as e:
                # Take "no module" as successfully loaded with PyTorch (it is importing)
                print(f"{file} uses PyTorch but cannot be loaded due to {e}, it's okay.")
            except: isPickle = False
        
        # Case 3: Restricted execution
        elif Path(file).suffix in {".npz", ".npy"}:
            try:
                with open(target, "rb") as f:
                    data = np.load(f, allow_pickle=False)
                    # For .npz files, we must force it to read an array to trigger the check
                    if target.endswith('.npz'):
                        for key in data.files:
                            _ = data[key]
                isPickle = False
            except Exception as e:
                if not "allow_pickle=" in str(e):
                    print(f"Error: Numpy loading failed due to a different issue: {e}")
                    isPickle = "unk"
        
        # Case 4: Check namelist
        elif Path(file).suffix == ".nemo":
            with tarfile.open(target, "r:*") as archive:
                files = archive.getnames()
                flag = False
                for f in files: 
                    if Path(f).suffix == ".ckpt": flag = True; break
                isPickle = flag
        
        # Delete the file if it is not Pickle, write the result
        if not isPickle: Path(target).unlink(missing_ok=True)
        if not has_files(path): shutil.rmtree(path, ignore_errors=True)
            
        with open(OUTPUT, "a") as f: 
            f.write(f"{repo['id']},{file},{isPickle},{status}\n")
