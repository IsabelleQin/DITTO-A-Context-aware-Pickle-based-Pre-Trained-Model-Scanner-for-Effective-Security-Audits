# DITTO-A-Context-aware-Pickle-based-Pre-Trained-Model-Scanner-for-Effective-Security-Audits
The replication package of "DITTO: A Context-aware Pickle-based Pre-Trained Model Scanner for Effective Security Audits"
<img src="ditto.png" alt="DITTO" width="100">

## Introduction
The expressive yet dangerous Pickle format is continuously used for Pre-trained model (PTM) exchange on public model hubs. To mitigate the security risks during Pickle-based PTM reuse, we present DITTO, a stack-based, context-aware scanner for Pickle-based PTMs. 

## Experiment Replication
This replication package contains the data and code for the two experiments (i.e., Hugging Face investigation and scanner evaluation; DITTO and scanner comparison) documented in our paper. 
To replicate our experiments, please first follow the instructions in ```./models/README.md``` to obtain the **PickleBench** dataset. 
The material and introduction for replicating **HF investigation and scanner evaluation** are stored under ```hf_investigation```; the material and introduction for replicating **DITTO and scanner comparison** are stored under ```baselines```. 

### Dependencies
- python>=3.11
- hf-xet=1.6.0
- huggingface-hub=1.27.0
- joblib
- fickling=1.12
- modelscan=0.8.8
- nemo-toolkit=3.0.0
- openai=2.53.0
- pandas
- picklescan=1.0.5
- pydantic
- torch=2.13.0
- tqdm
- transformers=5.14.1

## DITTO

DITTO comprises two major components: a ```trace generator``` and an ```intention analyzer```. The trace generator follows the intended framework loading path and safely emulates Pickle deserialization to capture security-sensitive PVM state transitions. The intention analyzer subsequently performs two stages. First, ```security-critical state extraction``` retains states and dependencies relevant to security analysis while removing routine reconstruction context. Then, ```context-aware intention analysis``` reasons about how the retained security-sensitive objects are used. DITTO produces context-aware, semantic-based reasoning and concise, deterministic security-critical states to facilitate human-in-the-loop security audits. Together, these components allow DITTO to automatically reason about behavior that would occur during deserialization without directly executing security-sensitive Pickle operations and provide contextual evidence for downstream security auditing. The implementation of the major components can be found under the ```components``` folder. 

## Usage
DITTO uses DeepSeek-V4-Flash, a state-of-the-art open-source model, as its default intention analyzer. 
In this replication package, we implement the model with the [DeepInfra API](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Flash). 
Please export the ```DEEPINFRA_TOKEN``` to your environment if you wish to execute DITTO directly. 
You may also adjust the LLM implementation in ```components/query.py``` if you wish to use DITTO with a local LLM or run with other inference platforms. 

### Example
A simple scanning example: 

```
python main.py -m models/malicious/ext_injection/ext_injection/inverted_registry.pkl
```

The intention analyzer will provide a detailed analysis such as 

```
{
  "assessment": "Likely malicious",
  "reasoning": "The trace shows a critical construction process where `copyreg._inverted_registry` is used to register code 1 as the `os.system` function. Then `pickle._Unpickler.get_extension(code=1)` is called with the argument `",
  "risky_trace": [
    {
      "target": "copyreg._inverted_registry",
      "contexts": "The registry is being modified to map extension code 1 to the `os.system` function. This is a deliberate setup to allow the unpickler to resolve code 1 to a dangerous system call during deserialization.",
      "intention": "Malicious"
    },
    {
      "target": "pickle._Unpickler.get_extension",
      "contexts": "The unpickler is retrieving the function associated with extension code 1, which has just been set to `os.system`. The call passes the string `",
      "intention": "Malicious"
    }
  ]
}
```

### Arguments

|Options|Description|
|---|---|
|```-mode/--loading_mode```|Specify the model loader for the PTM.|
|```-llm```|Specify the LLM for semantic analysis.|
|```--log_path```|Path to the full deserialization trace output.|
|```--extract_path```|Path to the extracted critical states.|
|```--analysis_path```|Path to the security analysis output.|

## Folder Structure
```
├── baselines  
    ├── analyze # Code for result analysis
    ├── execute # Code to execute scanners
    ├── results # Effectiveness and efficiency results of DITTO and the baseline scanners (RQ 1-3)
    ├── README.md
    ├── config.py # Experiment configuration
    └── utils.py
├── components
    ├── __init__.py
    ├── extract.py # Security-critical state extractor
    ├── generate.py # Deserialization trace generator
    ├── helper.py
    ├── hook.py
    └── query.py # Intention analyzer
├── emulation # PVM emulation helper                   
├── hf_investigation # Replication code and data for Section 3
    ├── repos
    ├── README.md
    ├── analyze.py
    ├── collect_repo.py
    ├── scanner_eval.py
    └── verify_pickle.py
├── models
    ├── benign # "HF Unscanned", "HF Unsafe", "PickleBall"
    ├── malicious # "Path Bypass", "Extension Injection", "PickleBall"
    ├── README.md
    ├── download_hf.py
    ├── download_pickleball.py
    └── hf_repos.csv
├── LICENSE
├── README.md
└── main.py
```
