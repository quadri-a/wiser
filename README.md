## Overview
This repository features the AI-assisted Wireless Systems Engineering and Research (WiSER) platform. 
WiSER is developed to facilitate intent-based wireless user scheduling and resource allocation (SRA). 
## Introduction and Main Contributions
In particular, we propose the Multi-Agent open source small/medium-sized Language Model (MAxLM)-based SRA for the Uplink of a multiuser (MU) MIMO-OFDMA-enabled WLAN. 
Figure below illustrates the modeling of the WLAN AP-STA connections as the agents and their interaction in the WLAN environment as a Markov Decision Process (MDP) problem. The MDP components are the agent, agent's state space, action space, and feedback.

<img width="1044" height="595" alt="sra_mdp" src="https://github.com/user-attachments/assets/16c4e78b-d2a2-4da5-a2da-b9c26ed99966" />

To orchestrate the workflow for autonomous SRA, WiSER is equipped with the following features:
1) Facilitates user's intent-based resource allocation strategy for multiple time-slotted wireless transmissions.
2) Performs SRA autonomously by using the Adaptive Context Management feature in the Context Manager to characterize the dynamically changing WLAN environment to the xLM.
3) Multi-agent realization enables the Scheduler (xLM) to asynchronously perform SRA and simplify complex resource optimization tasks.
4) Guarantees reliable parsing of the xLM's intent for SRA using the Parser.
5) Allows loading, storing, auditing network data, user's SRA intents, and xLM's response using the File Manager.
6) Render typical wireless environment/channel conditions using the Environment Manager.

## Installations
1. Open your terminal or Anaconda prompt and create your conda environment
```bash
conda create -n wiser python=3.11
conda activate wiser
```
2. Install LangGraph's Graph API
```bash
conda install conda-forge::langgraph-prebuilt
```
4. Download and Install Ollama Server
- Go to the Ollama Downloads Page.
- Choose the installer for your operating system (Windows, macOS, or Linux).
- Run the installer and complete the setup.
- Once installed, download a model by running this command in your command prompt:
    ```bash
   ollama run llama3.1
    ```
- Currently, WiSER implements the following open models:
  Instruct-based model: Llama3.1:8b
  Reasoning-based model: Mistral-NeMo:12b and Gemma:12b
7. Install packages (Async and Ollama)
```bash
 conda install -c conda-forge ollama python-dotenv –y
```
9. Install MATLAB engine API for Python
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
10.	Install Matplotlib
```bash
conda install matplotlib
```


