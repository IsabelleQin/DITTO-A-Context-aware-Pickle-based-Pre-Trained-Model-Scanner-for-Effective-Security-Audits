from huggingface_hub import HfApi
from datetime import datetime, timezone
import pandas as pd
from tqdm import tqdm
import json

# More than 1k downloads per month
MIN_DOWNLOAD = 1000
hf_api = HfApi()

# Check all popular repos in 2026
start = datetime(2025, 7, 1, tzinfo=timezone.utc)
end = datetime(2026, 6, 30, tzinfo=timezone.utc)
models = hf_api.list_models(sort="downloads", limit=25000, full=True)
all_repos = []
for model in tqdm(list(models)):
    if model.downloads < MIN_DOWNLOAD: break
    info = {
        "id": model.id,
        "downloads": model.downloads,
        "created_at": f"{model.created_at}",
        "tags": model.tags,
        "siblings": [s.rfilename for s in model.siblings]
    }
    
    if model.created_at >= start and model.created_at <= end: 
        all_repos.append(info)
with open("./hf_investigation/repos/all_repo.json", "w") as f:
    json.dump(all_repos, f, indent=4)
