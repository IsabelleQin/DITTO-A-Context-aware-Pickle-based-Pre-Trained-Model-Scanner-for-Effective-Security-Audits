import json
import sys
sys.path.append("./")
from baselines.config import *
from baselines.utils import *
import transformers
import os
import numpy as np
from tqdm import tqdm

# Tokenizer from DeepSeek official
chat_tokenizer_dir = "./baselines/analyze/deepseek_v3_tokenizer"
tokenizer = transformers.AutoTokenizer.from_pretrained(chat_tokenizer_dir, trust_remote_code=True)

trace_root = "./baselines/results/DITTO/full_trace"
extract_root = "./baselines/results/DITTO/critical_states"

# Construct the ground truth with model list
all_models = []
for model_list in model_lists:
    model_root = model_list["root"]
    label = model_list["label"]
    models = get_paths(f"{model_root}/{model_list['path']}")
    all_models.extend(models)
total = len(all_models)

results = {
    "Before": {"States": [], "Tokens": [], "Size": []}, 
    "After": {"States": [], "Tokens": [], "Size": []}
}

for i, model in enumerate(tqdm(all_models)):
    trace = f"{trace_root}/{model}.trace"
    extract = f"{extract_root}/{model}.states"
    # Continue if the model does not have extraction
    if not os.path.exists(extract): continue

    for (k, path) in (("Before", trace), ("After", extract)):
        # Check the number of states
        with open(path, "r") as f:
            lines = f.readlines()
        states = 0
        for line in lines:
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                states += 1
        results[k]["States"].append(states)

        # Check the number of tokens
        with open(path, "r") as f:
            result = tokenizer.encode(f.read())
            results[k]["Tokens"].append(len(result))

        # Check the file size
        size = os.path.getsize(path)
        results[k]["Size"].append(size/1024)

# Calculate max and avg
for state in ["Before", "After"]:
    for metric in ["States", "Tokens", "Size"]:
        print(f"{state}\n{metric}-avg: {np.mean(results[state][metric])}; max: {max(results[state][metric])}")
