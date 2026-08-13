import pandas as pd
from modelscan.modelscan import ModelScan
from picklescan import cli
import fickling
from fickling.fickle import Pickled
from fickling.pytorch import PyTorchModelWrapper

df = pd.read_csv("./hf_investigation/repos/has_pickle.csv")
ROOT = "./hf_investigation/repos/downloads"
OUTPUT = "./hf_investigation/repos/scanner_results.csv"

scanner = ModelScan()
with open(OUTPUT, 'w') as f:
    f.write("id,file,modelscan,picklescan,fickling\n")

for i, row in df.iterrows():
    if row["isPickle"] == "False": continue
    if not row["status"] in ("unscanned", "error", "unsafe"): continue
    target = f"{ROOT}/{row['id']}/{row['file']}"
        
    # Try scanning with the SOTA scanners
    # modelscan
    try: 
        results = scanner.scan(target)
        assert results["summary"]["scanned"]["total_scanned"] > 0 and not results["errors"]
        if results["summary"]["total_issues"] == 0: MS = "benign"
        else: MS = "malicious"
    except: MS = "failed"
    
    # Picklescan
    try:
        results = cli.scan_file_path(target)
        assert results.scanned_files > 0 and not results.scan_err
        # Have to check because it may not scan the globals..
        assert results.globals != []
        if results.infected_files == 0 and results.suspicious_count == 0: PS = "benign"
        else: PS = "malicious"
    except: PS = "failed"

    # Fickling
    try:
        try: model = PyTorchModelWrapper(target).pickled
        except Exception as e:
            with open(target, "rb") as pickle_file:
                    model = Pickled.load(pickle_file)
        results = fickling.analysis.check_safety(model).to_dict()
        assert results["detailed_results"]
        if results["severity"] == "LIKELY_SAFE": FKL = "benign"
        else: FKL = "malicious"
    except: FKL = "failed"
        
    with open(OUTPUT, "a") as f: f.write(f"{row['id']},{row['file']},{MS},{PS},{FKL}\n")
    
