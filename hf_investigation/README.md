## Hugging Face Investigation (Section 2.1)

### Collect Repo Info
We conducted a large-scale investigation of Pickle usage in 10,023 popular Hugging Face repositories created between July 1, 2025 and June 30, 2026. 
Each investigated repository has more than 1,000 monthly downloads (data collected on July 17, 2026). 
We run ```collect_repo.py``` to obtain the information about the recently created popular repositories, and the results are reported in ```repos/all_repo.json```. 

### Investigate Pickle-based PTMs
#### IMPORTANT!!! Since this step includes code execution, please execute the code in a separate Docker container!!!
We combine Hugging Face's Pickle scanning results with an additional verification process to investigate Pickle usage in the 10,023 repositories. 
We identify 9,544 Pickle-based PTMs across 929 repositories (9.3\%), demonstrating that Pickle remains prevalent in recently published and widely reused PTMs. 
Run ```verify_pickle.py``` to replicate this result. 
Since the HF API is needed to obtain Hugging Face's scanning results, please provide your ```HF_KEY``` before executing the code. 
The code should automatically download the 1,266 PTMs suspected of using Pickle and retain the 685 actual Pickle-based PTMs under ```models/benign/hf_unscanned```. 
```repos/has_pickle.csv``` summarizes our investigation results. 

We acknowledge that some maintainers may modify their repository and remove certain PTM files. 
To facilitate replication, we also provide the 685 Pickle-based PTMs directly. 

## Model Scanner Evaluation (Section 3.2)

We investigate the limitations of state-of-the-art model scanners with a total of 715 Pickle-based PTMs: 

1) 685 verified Pickle-based PTMs without valid Hugging Face scan results (*HF Unscanned*)
2) seven loading-path bypass examples from Liu et al. (*Path Bypass*)
3) our two extension-registry attacks (*Ext. Injection*)
4) 21 benign PTMs labeled "unsafe" by Hugging Face (*HF "Unsafe"*)

The 715 PTMs are provided under the ```models``` directory, and our evaluation result is stored as ```repos/scanner_results.csv```. 
Run ```scanner_eval.py``` to replicate the result. 
