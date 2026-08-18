## Evaluation (Section 6)

This directory contains our evaluation data and code to replicate our evaluation section. 

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
