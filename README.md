## Overview
This repository features the AI-assisted Wireless Systems Engineering and Research (WiSER) platform. 
WiSER is developed to facilitate intent-based wireless user scheduling and resource allocation (SRA). 
In particular, we have proposed the Multi-Agent open source small/medium-sized Language Model (MAxLM)-based SRA for the Uplink of a multiuser (MU) MIMO-OFDMA-enabled WLAN. 
Figure below illustrates the modeling of the AP-STA connections as the agents and their interaction in the WLAN environment as a Markov Decision Process (MDP) problem. The MDP components are the agent, agent's state space, action space, and feedback.

<img width="1744" height="1095" alt="sra_mdp" src="https://github.com/user-attachments/assets/16c4e78b-d2a2-4da5-a2da-b9c26ed99966" />

To orchestrate the workflow for autonomous SRA, WiSER is equipped with the following features:
1) Facilitates user's intent-based resource allocation strategy for multiple time-slotted wireless transmissions.
2) Performs SRA autonomously by using the Adaptive Context Management feature in the Context Manager to characterize the dynamically changing WLAN environment to the xLM.
3) Multi-agent realization enables the Scheduler (xLM) to asynchronously perform SRA and simplify complex resource optimization tasks.
4) Guarantees reliable parsing of the xLM's intent for SRA using the Parser.
5) Allows loading, storing, auditing network data, user's SRA intents, and xLM's response using the File Manager.
6) Render typical wireless environment/channel conditions using the Environment Manager.

## Quickstart


