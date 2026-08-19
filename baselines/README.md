## Evaluation (Section 6)

This directory contains our evaluation data and code to replicate our evaluation section. Our evaluation configurations (i.e., the data used and number of runs) are specified in ```baselines/config.py```. Instructions for preparing the data are documented in ```models/README.md```. 

### Execute the scanners

Run the following commands to scan PTMs with baseline scanners. 

```
python ./baselines/execute/eval_modelscan.py # ModelScan
python ./baselines/execute/eval_picklescan.py # PickleScan
python ./baselines/execute/eval_fickling.py # Fickling
```

```execute/eval_modelscan.py```, ```execute/eval_picklescan.py```, and ```execute/eval_fickling.py``` to scan the PTMs with baseline scanners. 
Their effectiveness and efficiency results are stored under the ```results/effectiveness``` and ```results/efficiency``` directories. 

To replicate DITTO's results, export the following API keys before execution: 

1. ```DEEPINFRA_TOKEN``` for default *DITTO* and *DITTO-w/o extraction*
2. ```OPENAI_API_KEY``` for *DITTO-GPT*
3. ```GEMINI_API_KEY``` for *DITTO-Gemini*

Run the following commands to execute DITTO and its variants.

```
# DITTO
python ./baselines/execute/eval_DITTO.py
# DITTO-w/o extraction
python ./baselines/execute/eval_DITTO_wo_extract.py
# DITTO-GPT
python ./baselines/execute/eval_DITTO.py -llm gpt-4.1-nano-2025-04-14
# DITTO-Gemini
python ./baselines/execute/eval_DITTO.py -llm gemini-3.1-flash-lite
```

DITTO's effectiveness results are stored under ```results/efficiency```, and the outputs generated during scanning (i.e., full trace, security-critical states, and the analysis report) are stored under the ```results/DITTO``` directory. 

### RQ1: End-to-End Effectiveness and RQ3: Ablation and Sensitivity

After obtaining all the scanner results (including DITTO's altered versions), run 

```python ./baselines/analysis/effectiveness.py``` 

and 

```python ./baselines/analysis/efficiency.py``` 

to calculate the effectiveness (SC, FPR, FNR, F1) and efficiency (time consumption) metrics. 
Run 

```python ./baselines/analysis/state_extraction.py``` 

to calculate the context and token reductions. 
The number of tokens is estimated with the official package provided by [DeepSeek](https://api-docs.deepseek.com/quick_start/token_usage/). 
We provide the original results reported in our paper in this repository. 

### RQ2: Context-Aware Analysis

We study DITTO's semantic analysis results in the paper. 
Given the stochastic nature of LLMs, the analysis results may not be perfectly consistent across each run. 
To ensure replicability, we also provide the analysis reports in ```results/DITTO```. 
