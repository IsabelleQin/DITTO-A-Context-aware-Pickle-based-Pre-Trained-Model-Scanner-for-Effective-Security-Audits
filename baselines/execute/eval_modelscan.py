from modelscan.modelscan import ModelScan
import time
import sys
sys.path.append("./")
from baselines.config import *
from baselines.utils import *
from tqdm import tqdm

time_output = f"{result_root}/efficiency/modelscan.csv"
with open(time_output, "w") as f:
    f.write("model,run,total\n")
scan_output = f"{result_root}/effectiveness/modelscan.csv"
with open(scan_output, "w") as f:
    f.write("model,run,label\n")
    
scanner = ModelScan()
for run in range(0, runs):
    for model_list in model_lists:
        model_root = model_list["root"]
        models = get_paths(f"{model_root}/{model_list['path']}")
        for model in tqdm(models):
            model_path = f"{model_root}/{model}"
            start = time.time()
            try:
                results = scanner.scan(model_path)
                assert results["summary"]["scanned"]["total_scanned"] > 0 and not results["errors"]
                if results["summary"]["total_issues"] == 0: label = 0
                else: label = 1
            except:
                label = -1
            end = time.time()
            with open(time_output, "a") as f:
                f.write(f"{model},{run},{end-start:.3f}\n")
            with open(scan_output, "a") as f:
                f.write(f"{model},{run},{label}\n")