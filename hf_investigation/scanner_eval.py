import pandas as pd
from modelscan.modelscan import ModelScan
from picklescan import cli
import fickling
from fickling.fickle import Pickled
from fickling.pytorch import PyTorchModelWrapper

# The four model sources
# 0 as benign, 1 as malicious
sources = {
    "./models/benign/hf_unscanned": 0,
    "./models/benign/hf_unsafe": 0,
    "./models/malicious/ext_injection": 1,
    "./models/malicious/path_bypass": 1,
}
OUTPUT = "./hf_investigation/repos/scanner_results.csv"
result = {
    "model": [], "groundtruth": [], "modelscan": [], "picklescan": [], "fickling": []
}

scanner = ModelScan()
for root, gt in sources.items():
    with open(f"{root}/model-list.txt", "r") as f:
        models = [l.strip() for l in f.readlines()]
    for model in models:
        result["model"].append(model)
        result["groundtruth"].append(gt)
        path = f"{root}/{model}"

        # modelscan
        try: 
            results = scanner.scan(path)
            assert results["summary"]["scanned"]["total_scanned"] > 0 and not results["errors"]
            if results["summary"]["total_issues"] == 0: result["modelscan"].append(0)
            else: result["modelscan"].append(1)
        except Exception as e: result["modelscan"].append(-1)
        
        # picklescan
        try:
            results = cli.scan_file_path(path)
            assert results.scanned_files > 0 and not results.scan_err
            # Have to check because it may not scan the globals..
            assert results.globals != []
            if results.infected_files == 0 and results.suspicious_count == 0: result["picklescan"].append(0)
            else: result["picklescan"].append(1)
        except: result["picklescan"].append(-1)
    
        # fickling
        try:
            try: model = PyTorchModelWrapper(path).pickled
            except Exception as e:
                with open(model, "rb") as pickle_file:
                        model = Pickled.load(pickle_file)
            results = fickling.analysis.check_safety(model).to_dict()
            # assert results["detailed_results"]
            if results["severity"] == "LIKELY_SAFE": result["fickling"].append(0)
            else: result["fickling"].append(1)
        except: result["fickling"].append(-1)

pd.DataFrame(result).to_csv(OUTPUT, index=None)
