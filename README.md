## Overview
This repository features the AI-assisted Wireless Systems Engineering and Research (WiSER) platform. 
WiSER is developed to facilitate intent-based wireless network management. 
In particular, we have developed a Multi-Agent open source small/medium-sized Language Model (MAxLM)-based user 
scheduling and resource allocation (SRA) scheme. Figure below illustrates the modeling of the AP-STA connections as the agents and their interaction with the WLAN environment as a Markov Decision Process (MDP) problem. 

<img width="1744" height="1095" alt="sra_mdp" src="https://github.com/user-attachments/assets/49be6f5d-e5f2-4ffe-a5bc-4055f691c6db" />

We have proposed the MAxLM-optimized SRA for the Uplink of a multiuser (MU) MIMO-OFDMA-enabled WLAN in our recent submission to IEEE Globecom 26.
The preprint of the submitted paper will be made available soon.
The main features of WiSER are listed below -
1) A multi-agent framework that enables an xLM to asynchronously perform SRA and simplify complex resource optimization tasks.
2) Facilitates user's intent-based resource allocation for multiple time-slotted wireless transmissions.
3) Achieves autonomous SRA by using the Adaptive Context Management feature that accurately characterizes the dynamically changing WLAN environment to the xLM.
4) Guarantees reliable parsing of the xLM's intent for SRA.
5) Allows loading, storing, auditing network data, user's SRA intents, and xLM's response with the file manager.

## Quickstart


