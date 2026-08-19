## Prepare Evaluation Data
The **PickleBench** dataset comprises 959 benign and 92 malicious models from validated real-world PTMs and representative deserialization attacks. 
The first part of PickleBench contains the 715 PTMs used for scanner evaluation (Section 3.2). 
The second part of PickleBench contains 336 PTMs derived from the PickleBall dataset. 
Please follow the instructions to obtain the PickleBench dataset. 

### Obtain the scanner evaluation dataset
1. **Malicious proof-of-concept**: We directly provide the seven "Path Bypass" and the two "Extension Injection" proof-of-concept models in this repository, under the ```malicious``` directory. 
   Code for generating these proof-of-concept examples is also provided under the same directory.
2. **Hugging Face PTMs**: We identify 685 unscanned benign PTMs and 21 false alerts during our Hugging Face investigation. 
   Since these models are generally large (a total of >400GB), we cannot provide the files directly. 
   Instead, we provide information about the exact models we used for evaluation in ```hf_repos.csv```, including the repository ID, file names, and the commit version. 
   Run
   
   ```
   python ./models/download_hf.py
   ```
   
   to obtain the 706 models. 
   The "HF Unscanned" and "HF Unsafe" models will be stored under the ```benign``` repository. 

### Prepare the PickleBall dataset
Run 

```
python ./models/download_pickleball.py
```

to download the [PickleBall dataset](https://zenodo.org/records/16974645). 
The benign and malicious tarballs will be stored under ```benign/pickleball``` and ```malicious/pickleball```, respectively. 
Afterwards, follow the instructions in [PickleBall's replication package](https://github.com/columbia/pickleball/tree/main/evaluation) to extract models from the tarballs. 
Then, remove ```oceanhacktitude/tinymodel/tinymodel/twitter-roberta-base-sentiment.bin``` from ```malicious/pickleball/model-list.txt```. 
As mentioned in our paper, this model does not demonstrate malicious behavior during deserialization. Thus, we exclude it from the malicious collection. 
