import time
import logging
import sys
from pathlib import Path
sys.path.append("./")
from baselines.utils import *
from baselines.config import *
from tqdm import tqdm
from components import hook
hook()
from components import *
import argparse

if __name__ == "__main__":
    logger = logging.getLogger("evaluation")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    parser = argparse.ArgumentParser(description="Security scanner detecting Python Pickle files performing suspicious actions.")
    parser.add_argument("-llm", help="The LLM specified for inference", default="DeepSeek-V4-Flash-0731")
    args = parser.parse_args()

    Path(f"{result_root}/DITTO_{args.llm}.log").unlink(missing_ok=True)
    set_handler(logger, f"{result_root}/noextract_DITTO_{args.llm}.log", "a")

    time_output = f"{result_root}/efficiency/DITTO_noextract_{args.llm}.csv"
    with open(time_output, "w") as f:
        f.write("model,run,generate,analyze,total\n")

    for run in range(0, runs):
        logger.info(f"Starting run {run}...")
        for model_list in model_lists:
            model_root = model_list["root"]
            models = get_paths(f"{model_root}/{model_list['path']}")
            for model in tqdm(models):
                logger.info(f"Checking model {model}")
                # Prepare for scanning
                model_path = f"{model_root}/{model}"
                log_path = f"{result_root}/DITTO/full_trace/{model}.trace"
                Path(log_path).parent.mkdir(parents=True, exist_ok=True)

                # Start generating the full trace
                start = time.time()
                scan(model_path, log_path, None)
                end = time.time()
                gen_time = end-start

                # Check whether we need to query the LLM - If no query needed, then the model is safe
                if not getquery(): 
                    with open(time_output, "a") as f:
                        f.write(f"{model},{run},{gen_time:.3f},0,{gen_time:.3f}\n")
                else:
                    # Prepare for query
                    analysis_path = f"{result_root}/DITTO/{args.llm}/{model}_run{run}.json"
                    Path(analysis_path).parent.mkdir(parents=True, exist_ok=True)
                        
                    # Compress the log and extract risky states
                    start = time.time()
                    query(args.llm, log_path, analysis_path)
                    end = time.time()
                    analyze_time = end-start
                    full_time = gen_time+analyze_time
                    with open(time_output, "a") as f:
                        f.write(f"{model},{run},{gen_time:.3f},{analyze_time:.3f},{full_time:.3f}\n")