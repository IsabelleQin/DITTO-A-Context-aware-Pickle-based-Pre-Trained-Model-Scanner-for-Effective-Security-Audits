from modelscan.modelscan import ModelScan
import time
import sys
sys.path.append("./")
from baselines.config import *
from baselines.utils import *
from tqdm import tqdm

time_output = f"{result_root}/modelscan_efficiency.csv"
with open(time_output, "w") as f:
    f.write("model,run,total\n")
scan_output = f"{result_root}/modelscan_effectiveness.csv"
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
                if results["summary"]["total_issues"] == 0: label = "benign"
                else: label = "malicious"
            except:
                label = "failed"
            end = time.time()
            with open(time_output, "a") as f:
                f.write(f"{model},{run},{end-start:.3f}\n")
            with open(scan_output, "a") as f:
                f.write(f"{model},{run},{label}\n")