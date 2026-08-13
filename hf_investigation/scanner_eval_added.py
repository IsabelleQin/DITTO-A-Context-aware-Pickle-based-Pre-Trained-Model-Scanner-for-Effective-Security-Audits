from modelscan.modelscan import ModelScan
from picklescan import cli
import fickling
from fickling.fickle import Pickled
from fickling.pytorch import PyTorchModelWrapper

ROOT = "./hf_investigation/repos/added/added"
FILES = {
    "bz22pickle.joblib", "gzip2pickle.joblib", "lz42pickle.joblib",
    "lzma2pickle.joblib", "xz2pickle.joblib", "zlib2pickle.joblib",
    "inverted_registry.pkl", "add_extension.pkl", "tar2pickle.tar",
}
OUTPUT = "./hf_investigation/repos/scanner_results.csv"

scanner = ModelScan()

for file in FILES:
    target = f"{ROOT}/{file}"
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
        
    with open(OUTPUT, "a") as f: f.write(f"added,{file},{MS},{PS},{FKL}\n")
    