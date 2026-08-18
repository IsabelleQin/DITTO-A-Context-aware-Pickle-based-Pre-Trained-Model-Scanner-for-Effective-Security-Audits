## Evaluation (Section 6)

This directory contains our evaluation data and code to replicate our evaluation section. Our evaluation configurations (i.e., the data used and number of runs) are specified in ```baselines/config.py```. 

### Data Preparation

The PickleBench dataset comprises 959 benign and 92 malicious models from validated real-world PTMs and representative deserialization attacks. 
The first part of PickleBench contains the 715 PTMs used for scanner evaluation (Section 3.2). 
The second part of PickleBench contains 336 PTMs derived from the PickleBall dataset. 
Please download and decompress the second part from [PickleBall's replication package](https://zenodo.org/records/16974645). 
After obtaining the PickleBall dataset, remove ```oceanhacktitude/tinymodel/tinymodel/twitter-roberta-base-sentiment.bin``` from ```malicious/model-list.txt```. 
This model does not demonstrate malicious behavior during deserialization. Thus, we exclude it from the malicious collection. 
Finally, move the models under PickleBall's benign and malicious directories to ```models/benign/pickleball``` and ```models/malicious/pickleball```, respectively.

### Execute the scanners

Run ```eval_modelscan.py```, ```eval_picklescan.py```, and ```eval_fickling.py``` to scan the PTMs with baseline scanners. 
Their effectiveness and efficiency results are stored under the ```results/effectiveness``` and ```results/efficiency``` directories. 
To replicate DITTO's results, export these API keys before execution: ```DEEPINFRA_TOKEN``` for default DITTO, ```OPENAI_API_KEY``` for DITTO-GPT, and ```GEMINI_API_KEY``` for DITTO-Gemini. 
DITTO's effectiveness results are stored under ```results/efficiency```, and the outputs generated during scanning (i.e., full trace, security-critical states, and the analysis report) are stored under the ```results/DITTO``` directory. 

### RQ1: End-to-End Effectiveness and RQ3: Ablation and Sensitivity

After obtaining all the scanner results (including DITTO's altered versions), run ```baselines/analysis/effectiveness.py``` and ```baselines/analysis/efficiency.py``` to calculate the effectiveness (SC, FPR, FNR, F1) and efficiency (time consumption) metrics. 
Run ```baselines/analysis/state_extraction.py``` to calculate the context and token reductions. 
The number of tokens is estimated with the official package provided by [DeepSeek](https://api-docs.deepseek.com/quick_start/token_usage/). 
We provide the original results reported in our paper in this repository. 

### RQ2: Context-Aware Analysis

We study DITTO's semantic analysis results in the paper. 
Given the stochastic nature of LLMs, the analysis results may not be perfectly consistent across each run. 
To ensure replicability, we also provide the analysis reports in ```results/DITTO```. 
