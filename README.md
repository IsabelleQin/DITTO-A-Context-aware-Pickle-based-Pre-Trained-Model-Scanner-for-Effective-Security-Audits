# DITTO-A-Context-aware-Pickle-based-Pre-Trained-Model-Scanner-for-Effective-Security-Audits
The replication package of "DITTO: A Context-aware Pickle-based Pre-Trained Model Scanner for Effective Security Audits"

## Introduction
The expressive yet dangerous Pickle format is continuously used for Pre-trained model (PTM) exchange on public model hubs. To mitigate the security risks during Pickle-based PTM reuse, we present DITTO, a stack-based, context-aware scanner for Pickle-based PTMs. 

## Experiment Replication

### Dependencies
- python>=3.11
- torch
- numpy
- fickling>=1.10
- modelscan
- picklescan

## Experiment Replication

### General Guideline


### Baseline Scanners
We compare DITTO with three state-of-the-art static scanners, implemented with their GitHub instructions. 

- **[PickleScan](https://github.com/mmaitre314/picklescan)**: We use ``picklescan.cli.scan_file_path`` for model file scanning. 
- **[ModelScan](https://github.com/protectai/modelscan)**: We initialize a scanner with ``ModelScan`` to scan all model files.
- **[Fickling](https://github.com/trailofbits/fickling)**: We attempt to use ``PyTorchModelWrapper`` to load each model file. If failed, we fall back to its ``Pickled`` module for loading. Then, we use ``fickling.analysis.check_safety`` to detect and output anomalous behaviors.

## DITTO

DITTO comprises two major components: a ```trace generator``` and an ```intention analyzer```. The trace generator follows the intended framework loading path and safely emulates Pickle deserialization to capture security-sensitive PVM state transitions. The intention analyzer subsequently performs two stages. First, ```security-critical state extraction``` retains states and dependencies relevant to security analysis while removing routine reconstruction context. Then, ```context-aware intention analysis``` reasons about how the retained security-sensitive objects are used. DITTO produces context-aware, semantic-based reasoning and concise, deterministic security-critical states to facilitate human-in-the-loop security audits. Together, these components allow DITTO to automatically reason about behavior that would occur during deserialization without directly executing security-sensitive Pickle operations and provide contextual evidence for downstream security auditing. 

## Usage

## Repo Structure


The ``baseline`` folder provides codes to execute DITTO and the three baseline scanners. The four scanners execute three runs by default. 
