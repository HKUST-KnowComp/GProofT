# GProofT: A Multi-dimension Multi-round Fact Checking Framework Based on Claim Fact Extraction

This is the official code and data repository for the [EMNLP 2024 Workshop FEVER AVeriTeC Shared Task](https://fever.ai/) paper:
[GProofT: A Multi-dimension Multi-round Fact Checking Framework Based on Claim Fact Extraction](https://arxiv.org/abs/2401.07286).
**[the url of the paper needs to be updated].**

![Overview](**The path needs to be updated**)

## 1. Requirements

we use python 3.9.19 which suits all packages

Requirements:
```
spaCy==3.7.5
pandas==2.2.2
openai
transformers==4.20.1
google-auth==2.31.0
```

## 2. GProofT Framework

The code for implementing GProofT framework is **[path needed to be updated]**.

Replace the OpenAI key and Google Search API key with your own ones in the code to execute the fact-checking process.
<!--can be downloaded
at [this link](https://hkustconnect-my.sharepoint.com/:f:/g/personal/wwangbw_connect_ust_hk/EqhEyfccW45HtyehVTDO_cgB9A2X4TQQKdeVnjqK1wMgng).-->

## 3. 
1. llama_eval.py
This script is used to call large language models like LLaMA3 and LLaMA3-Instruct from Hugging Face to run zero_shot experiment and generate verdicts. For instructions on fine-tuning the model, you can refer to the link https://github.com/hiyouga/LLaMA-Factory.

2. Data_Processing
This directory contains code for data processing. It includes scripts to combine the verdict with retrieved evidence and restructure the data to fit a fine-tuning framework. You may use these scripts as needed if they are helpful for your specific tasks.

## 4. 

## 5. Citing this work

Please use the bibtex below for citing our paper:

<```bibtex
@inproceedings{GProofT,
        author = {Jiayu Liu and
                  Junhao Tang and
                  Hanwen Wang and
                  Baixuan Xu and
                  Haochen Shi and
                  Weiqi Wang and
                  Yangqiu Song},
        title = {{GProofT:} A Multi-dimension Multi-round Fact Checking Framework Based on Claim Fact Extraction
},
        year = {2024},
        booktitle = {The Seventh Workshop on Fact Extraction and VERification - AVeriTeC Shared Task, {FEVER} 2024}
}
```>

## 6. Acknowledgement

The authors of this paper were supported by the NSFC Fund (U20B2053) from the NSFC of China, the RIF (R6020-19 and R6021-20), and the GRF (16211520 and 16205322) from RGC of Hong Kong. We also thank the support from the UGC Research Matching Grants (RMGS20EG01-D, RMGS20CR11, RMGS20CR12, RMGS20EG19, RMGS20EG21, RMGS23CR05, RMGS23EG08). 
