import pandas as pd
import numpy as np
import sys
sys.path.append("./")
from baselines.config import *
from baselines.utils import *

baselines = ["fickling", "modelscan", "picklescan"]
llms = ["DeepSeek-V4-Flash-0731", "noextract_DeepSeek-V4-Flash-0731", "gemini-3.1-flash-lite", "gpt-4.1-nano-2025-04-14"]
ditto_variants = [f"DITTO_{llm}" for llm in llms]

overall = {}
DITTO_components = {}
for tool in baselines+ditto_variants:
    print("="*10)
    result = pd.read_csv(f"./baselines/results/efficiency/{tool}.csv")
    # Check overall
    print(f"{tool} Total\nmax: {result['total'].max():.3f}, mean: {result['total'].mean():.3f}")

    # Check DITTO components
    if not tool.startswith("DITTO"): continue
    print(f"{tool} Generate\nmax: {result['generate'].max():.3f}, mean: {result['generate'].mean():.3f}")
    print(f"{tool} Analyze\nmax: {result['analyze'].max():.3f}, mean: {result['analyze'].mean():.3f}")
