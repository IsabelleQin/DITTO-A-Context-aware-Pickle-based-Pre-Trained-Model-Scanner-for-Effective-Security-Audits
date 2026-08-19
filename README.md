# DITTO-A-Context-aware-Pickle-based-Pre-Trained-Model-Scanner-for-Effective-Security-Audits
The replication package of "DITTO: A Context-aware Pickle-based Pre-Trained Model Scanner for Effective Security Audits"

## Introduction
The expressive yet dangerous Pickle format is continuously used for Pre-trained model (PTM) exchange on public model hubs. To mitigate the security risks during Pickle-based PTM reuse, we present DITTO, a stack-based, context-aware scanner for Pickle-based PTMs. 

## Experiment Replication

This replication package contains the data and code for the two experiments (i.e., Hugging Face investigation and scanner evaluation; DITTO and scanner comparison) documented in our paper. The material and introduction for replicating **HF investigation and scanner evaluation** are stored under ```hf_investigation```; the material and introduction for replicating **DITTO and scanner comparison** are stored under ```baselines```.

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

## Repo Structure


The ``baseline`` folder provides codes to execute DITTO and the three baseline scanners. The four scanners execute three runs by default. 
