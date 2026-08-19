# The models for experiments
# We use 0 for benign models, 1 for malicious models
# A scanner predicts "-1" if it fails to scan a model

model_lists = [
    {
        "label": 0,
        "root": "./models/benign/hf_unscanned",
        "path": "model-list.txt"
    },
    {
        "label": 0,
        "root": "./models/benign/hf_unsafe",
        "path": "model-list.txt"
    },
    {
        "label": 0,
        "root": "./models/benign/pickleball",
        "path": "model-list.txt"
    },
    {
        "label": 1,
        "root": "./models/malicious/ext_injection",
        "path": "model-list.txt"
    },
    {
        "label": 1,
        "root": "./models/malicious/path_bypass",
        "path": "model-list.txt"
    },
    {
        "label": 1,
        "root": "./models/malicious/pickleball",
        "path": "model-list.txt"
    }
]

result_root = "./baselines/results"
# The number of repetitive runs
runs = 3

