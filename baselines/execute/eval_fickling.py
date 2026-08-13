import time
import fickling
import sys
sys.path.append("./")
from fickling.fickle import Pickled
from fickling.pytorch import PyTorchModelWrapper
from baselines.config import *
from baselines.utils import *
from tqdm import tqdm
time_output = f"{result_root}/fickling_efficiency.csv"
with open(time_output, "w") as f:
    f.write("model,run,total\n")
scan_output = f"{result_root}/fickling_effectiveness.csv"
with open(scan_output, "w") as f:
    f.write("model,run,label\n")

fickling.hook.activate_safe_ml_environment()
fickling.always_check_safety()
    
for run in range(0, runs):
    for model_list in model_lists:
        model_root = model_list["root"]
        models = get_paths(f"{model_root}/{model_list['path']}")
        for model_name in tqdm(models):
            model_path = f"{model_root}/{model_name}"
            start = time.time()
            try:
                try: model = PyTorchModelWrapper(model_path).pickled
                except Exception as e:
                    with open(model_path, "rb") as pickle_file:
                            model = Pickled.load(pickle_file)
                results = fickling.analysis.check_safety(model).to_dict()
                assert results["detailed_results"]
                if results["severity"] == "LIKELY_SAFE": label = "benign"
                else: label = "malicious"
            except: 
                label = "failed"
            end = time.time()
            with open(time_output, "a") as f:
                f.write(f"{model_name},{run},{end-start:.3f}\n")
            with open(scan_output, "a") as f:
                f.write(f"{model_name},{run},{label}\n")