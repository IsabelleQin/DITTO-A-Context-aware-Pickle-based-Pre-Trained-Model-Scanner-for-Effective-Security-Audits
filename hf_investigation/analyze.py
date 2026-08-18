import pandas as pd

# The four model sources
# 0 as benign, 1 as malicious
sources = {
    "./models/benign/hf_unscanned": 0,
    "./models/benign/hf_unsafe": 0,
    "./models/malicious/ext_injection": 1,
    "./models/malicious/path_bypass": 1,
}
scanners = ["modelscan", "picklescan", "fickling"]
df = pd.read_csv("./hf_investigation/repos/scanner_results.csv")

for root, gt in sources.items():
    result = {s: {"FP": 0, "FN": 0, "Scanned": 0} for s in scanners}
    with open(f"{root}/model-list.txt", "r") as f:
        models = [l.strip() for l in f.readlines()]

    # To calculate the metrics
    total = len(models)
    benign = len(models) if gt == 0 else 0
    malicious = len(models) if gt == 1 else 0

    for model in models:
        row = df[df["model"] == model].iloc[0]
        for s in scanners:
            if row[s] == -1: continue
            result[s]["Scanned"] += 1
            if row[s] == 0 and row["groundtruth"] == 1:
                result[s]["FN"] += 1
            elif row[s] == 1 and row["groundtruth"] == 0:
                result[s]["FP"] += 1
                
    print(f"{root}, total benign: {benign}; total malicious: {malicious}")
    for s in scanners:
        print(s)
        print(f"{result[s]['Scanned']} / {result[s]['FP']} / {result[s]['FN']}")