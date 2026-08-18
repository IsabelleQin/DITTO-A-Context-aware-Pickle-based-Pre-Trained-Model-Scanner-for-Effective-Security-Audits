import json
import pandas as pd
import sys
sys.path.append("./")
from baselines.config import *
from baselines.utils import *
import numpy as np

# Construct the ground truth with model list
ground_truths = {}
total, benign, malicious = 0, 0, 0
for model_list in model_lists:
    model_root = model_list["root"]
    label = model_list["label"]
    models = get_paths(f"{model_root}/{model_list['path']}")
    for model in models:
        ground_truths[model] = label
        total += 1
        if label == 0: benign += 1
        else: malicious += 1

baselines = ["fickling", "modelscan", "picklescan"]
llms = ["DeepSeek-V4-Flash-0731", "noextract_DeepSeek-V4-Flash-0731", "gemini-3.1-flash-lite", "gpt-4.1-nano-2025-04-14"]
ditto_variants = [f"DITTO_{llm}" for llm in llms]

perf = {tool: 
    {metric: [0, 0, 0] for metric in ["Coverage", "TP", "FP", "TN", "FN", 
                                      "SC", "FPR", "FNR", "F1"]}
    for tool in baselines+ditto_variants} 

# Check baselines
for tool in baselines:
    df = pd.read_csv(f"./baselines/results/effectiveness/{tool}.csv")
    for i, row in df.iterrows():
        model = row["model"]
        run = row["run"]
        label = ground_truths[model]
        # Not scanned, pass
        if row["label"] == -1: continue

        # Scanning coverage
        perf[tool]["Coverage"][run] += 1
        # Effectiveness metrics
        if row["label"] == 1 and label == 1: 
            perf[tool]["TP"][run] += 1
        elif row["label"] == 1 and label == 0: 
            perf[tool]["FP"][run] += 1
        elif row["label"] == 0 and label == 0: 
            perf[tool]["TN"][run] += 1
        elif row["label"] == 0 and label == 1: 
            perf[tool]["FN"][run] += 1
        else: raise ValueError("Should never have this??")
        
# Check DITTO
for llm in llms:
    ditto = f"DITTO_{llm}"
    for run in range(runs):
        for model, label in ground_truths.items():
            path = f"./baselines/results/DITTO/{llm}/{model}_run{run}.json"
            try:
                with open(path, "r") as f:
                    res = json.load(f)
                    assessment = res["assessment"]
            except:
                assessment = "Likely benign"
            if assessment == "Unknown due to an error": continue

            # Scanning coverage
            perf[ditto]["Coverage"][run] += 1
            if assessment == "Likely malicious" and label == 1: 
                perf[ditto]["TP"][run] += 1
            elif assessment == "Likely malicious" and label == 0: 
                perf[ditto]["FP"][run] += 1
            elif assessment == "Likely benign" and label == 0: 
                perf[ditto]["TN"][run] += 1
            elif assessment == "Likely benign" and label == 1: 
                perf[ditto]["FN"][run] += 1
            else: raise ValueError("Should never have this??")

# Calculate results
results = {"Tool": [], "Coverage": [], "SC": [], "FPR": [], "FNR": [], "F1": []}
for tool in baselines+ditto_variants:
    results["Tool"].append(tool)
    for run in range(runs):
        perf[tool]["SC"][run] = perf[tool]["Coverage"][run]/total
        perf[tool]["FPR"][run] = perf[tool]["FP"][run]/(perf[tool]["FP"][run]+perf[tool]["TN"][run])
        perf[tool]["FNR"][run] = perf[tool]["FN"][run]/(perf[tool]["FN"][run]+perf[tool]["TP"][run])
        
        precision = perf[tool]["TP"][run]/(perf[tool]["TP"][run]+perf[tool]["FP"][run])
        recall = perf[tool]["TP"][run]/(perf[tool]["TP"][run]+perf[tool]["FN"][run])
        perf[tool]["F1"][run] = 2*precision*recall/(precision+recall)

    for metric in ["Coverage", "SC", "FPR", "FNR", "F1"]:
        avg = np.mean(perf[tool][metric])
        if metric == "Coverage": avg = int(avg)
        results[metric].append(avg)

pd.DataFrame(results).to_csv("./baselines/results/summary_effectiveness.csv", float_format='%.3f', index=None)
