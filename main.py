import logging
import sys
import argparse
from components import hook
hook()
from components import *

__all__ = ["scan", "extract"]
logger = logging.getLogger(f"StaticUnpickler")

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    parser = argparse.ArgumentParser(description="Security scanner detecting Python Pickle files performing suspicious actions.")
    parser.add_argument("-m", 
                            "--model_path", 
                            help="Path to the file or folder to scan", 
                            dest="model_path",
                            required=True)
    parser.add_argument("-mode",
                            "--loading_mode",
                            type=str,
                            help="Specify the model loader for the PTM.", 
                            dest="mode",
                            default=None)
    parser.add_argument("-llm",
                            type=str,
                            help="Specify the LLM for semantic analysis.", 
                            dest="llm",
                            default="DeepSeek-V4-Flash-0731")
    parser.add_argument("--log_path",
                            type=str,
                            help="Path to the full deserialization trace output.", 
                            dest="log_path",
                            default="full_trace.log")
    parser.add_argument("--extract_path",
                            type=str,
                            help="Path to the extracted critical states.", 
                            dest="extract_path",
                            default="critical_states.txt")
    parser.add_argument("--analysis_path",
                            type=str,
                            help="Path to the security analysis output.", 
                            dest="analysis_path",
                            default="analysis.json")
    args = parser.parse_args()
    logger.info(f'Scanning model: {args.model_path}')
    
    scan(args.model_path, args.log_path, args.mode)
    # Stop scanning if it is safe
    if getquery():
        extract(args.log_path, args.extract_path)
        query(args.llm, args.extract_path, args.analysis_path)
    else:
        print("The model is likely safe! No unknown or risky callable is used. ")