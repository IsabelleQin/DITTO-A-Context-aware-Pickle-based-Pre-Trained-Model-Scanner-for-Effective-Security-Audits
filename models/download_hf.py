from huggingface_hub import hf_hub_download
import pandas as pd

results = {
    "id": [], "file": [], "sha": [], "source": []
}

# Download the ``unsafe'' and unscanned files
stat = pd.read_csv("./models/hf_repos.csv")
for i, row in stat.iterrows():
    try:
        hf_hub_download(
            repo_id=row["id"], 
            filename=row["file"], 
            revision=row["sha"],
            local_dir=f"./models/benign/{row['source']}"
            )
    except Exception as e:
        print(e)