## Overview
This repository features the AI-assisted Wireless Systems Engineering and Research (WiSER) platform. WiSER is designed to facilitate the convenient integration of open-source language models for wireless systems research and development.
## Wireless Systems Research: AI-assisted Scheduling & Resource Allocation (SRA)
In our recent work, we have developed the Multi-Agent open source small/medium-sized Language Model (MAxLM)-based SRA scheme for MU-MIMO-OFDMA-enabled Networks. To perform SRA, WiSER implements the following open models and runs on a server equipped with the NVIDIA GeForce RTX 2080 Ti GPU (12GB VRAM):
  - Instruct-based model: Llama3.1:8b
  - Reasoning-based model: Mistral-NeMo:12b and Gemma:12b
    
Please cite the [paper on MAxLM-optimized SRA](https://arxiv.org/pdf/2605.16144), if you use the MA framework and WiSER platform.
@article{quadri2026maxlm,
  title={MAxLM: Multi-Agent Language Model-Based Scheduling and Resource Allocation in MU-MIMO-OFDMA-Enabled Wireless Networks},
  author={Quadri, Adnan and Li, Hongxiang},
  journal={arXiv preprint arXiv:2605.16144},
  year={2026}
}

<div align="center"><figure>
  <img width="650" src="https://github.com/user-attachments/assets/3b283426-0c98-4d80-83a7-480b4bf7cc9b" alt="Agent-Environment interaction modeled as Markov Decision Process (MDP) problem"> 
  
  <p align="center"><sub>Figure 1: The WLAN AP-STA connections are the agents and their interaction with the WLAN environment is modeled as a Markov Decision Process (MDP) problem.</sub></p>
</figure></div>

## Main Contributions
To orchestrate the workflow for autonomous SRA, WiSER is equipped with the following features:

1) Facilitates a user’s intent-based SRA strategy for multiple time-slotted wireless transmissions.
2) The Adaptive Context Management feature in the Context Manager enables the xLM to anticipate effective SRA strategies.
3) Multi-agent realization enables the xLM to perform SRA in a decentralized manner, simplifying complex optimization problems.
4) The Parser module guarantees reliable interpretation of the xLM’s intent for SRA.
5) The File Manager loads, stores, and audits network data, user SRA intents, and xLM responses, respectively.
6) The Environment Manager simulates wireless environment and channel conditions.

## Dependencies
1. Open your terminal or Anaconda prompt and create your conda environment
```bash
conda create -n wiser python=3.11
conda activate wiser
git clone https://github.com/quadri-a/wiser.git
cd wiser
python wiser.py
```
2. Install LangGraph's Graph API
```bash
conda install conda-forge::langgraph-prebuilt
```
3. Download and Install Ollama Server
- Go to the Ollama Downloads Page.
- Choose the installer for your operating system (Windows, macOS, or Linux).
- Run the installer and complete the setup.
- Once installed, download a model by running this command in your command prompt:
    ```bash
   ollama run llama3.1
    ```
4. Install packages (Async and Ollama)
```bash
 conda install -c conda-forge ollama python-dotenv –y
```
5. Install MATLAB engine API for Python
- Open MATLAB.In the Command Window, type matlabroot and press Enter.
- Copy the returned path (e.g., C:\Program Files\MATLAB\R2023b).
- In your terminal (with the Conda environment still active), navigate to the Python engine folder:
  For Windows:
```bash
cd "matlabroot\extern\engines\python
```
  For macOS/Linux:
```bash
cd "matlabroot/extern/engines/python
```
- Run the installation command:
```bash
python -m pip install
```
- For MATLAB version R2022b and later:
 ```bash
 python -m pip install matlabengine
 ```
6.	Install Matplotlib
```bash
conda install matplotlib
```


