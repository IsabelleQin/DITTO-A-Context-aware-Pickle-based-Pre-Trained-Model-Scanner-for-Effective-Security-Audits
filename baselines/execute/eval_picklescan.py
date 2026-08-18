import time
import sys
sys.path.append("./")
from baselines.config import *
from baselines.utils import *
from picklescan import cli
from tqdm import tqdm

time_output = f"{result_root}/efficiency/picklescan.csv"
with open(time_output, "w") as f:
    f.write("model,run,total\n")
scan_output = f"{result_root}/effectiveness/picklescan.csv"
with open(scan_output, "w") as f:
    f.write("model,run,label\n")
    
for run in range(0, runs):
    for model_list in model_lists:
        model_root = model_list["root"]
        models = get_paths(f"{model_root}/{model_list['path']}")
        for model in tqdm(models):
            model_path = f"{model_root}/{model}"
            start = time.time()
            results = None
            try:
                results = cli.scan_file_path(model_path)
                assert results.scanned_files != 0
                if results.scan_err: label = -1
                elif results.infected_files != 0 or results.suspicious_count != 0: label = 1
                else: 
                    assert results.globals != []
                    label = 0
            except: label = -1
            end = time.time()
            with open(time_output, "a") as f:
                f.write(f"{model},{run},{end-start:.3f}\n")
            with open(scan_output, "a") as f:
                f.write(f"{model},{run},{label}\n")