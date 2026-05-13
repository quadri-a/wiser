## Overview
This repository features the AI-assisted Wireless Systems Engineering and Research (WiSER) platform. 
WiSER is developed to facilitate convenient integration of open source Language Models for wireless systems research and development. 
## Wireless Systems Research: AI-assisted Scheduling & Resource Allocation (SRA)
In our recent work, we have developed the Multi-Agent open source small/medium-sized Language Model (MAxLM)-based SRA scheme for the Uplink of a multiuser (MU) MIMO-OFDMA-enabled WLAN. To perform SRA, WiSER implements the following open models and runs on a server equipped with the NVIDIA GeForce RTX 2080 Ti GPU (12GB VRAM):
  - Instruct-based model: Llama3.1:8b
  - Reasoning-based model: Mistral-NeMo:12b and Gemma:12b

<div align="center"><figure>
  <img width="650" src="https://github.com/user-attachments/assets/16c4e78b-d2a2-4da5-a2da-b9c26ed99966" alt="Agent-Environment Interaction modeled as MDP"> 
  
  <p align="center"><sub>Figure 1: The WLAN AP-STA connections are the agents and their interaction with the WLAN environment is modeled as a Markov Decision Process (MDP) problem.</sub></p>
</figure></div>

## Main Contributions

To orchestrate the workflow for autonomous SRA, WiSER is equipped with the following features:
1) Facilitates user's intent-based resource allocation strategy for multiple time-slotted wireless transmissions.
2) Performs SRA autonomously by using the Adaptive Context Management feature in the Context Manager to characterize the dynamically changing WLAN environment to the xLM.
3) Multi-agent realization enables the Scheduler (xLM) to asynchronously perform SRA and simplify complex resource optimization tasks.
4) Guarantees reliable parsing of the xLM's intent for SRA using the Parser.
5) Allows loading, storing, auditing network data, user's SRA intents, and xLM's response using the File Manager.
6) Render typical wireless environment/channel conditions using the Environment Manager.

## Dependencies
1. Open your terminal or Anaconda prompt and create your conda environment
```bash
conda create -n wiser python=3.11
conda activate wiser
git clone https://github.com/quadri-a/wiser.git
cd wiser
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


