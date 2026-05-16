#numpy libraries
import numpy as np
# MATLAB Engine
import matlab.engine

#Langgraph packages 
from langgraph.graph import START, END, StateGraph
from wiser_state_schema import (
    AgentState, 
    StateInput, 
    StateOutput,
    )

#WiSER modules realized as classes
from Context_Manager import AdaptiveContextManagement
from scheduler import scheduling_engine
from parser import ModelOutputParser
from Environment_Manager import EnvironmentManager
from File_Manager import FileManager

#Structured Output
from wiser_modular_prompts import (
    json_schema_for_SRA,
    )
# Intent-based Scheduling Strategies
from intent_based_strategies import(
    BCQ,
    MAxLM,
    )
#Packages for asynchronous operations
from ollama import AsyncClient
import nest_asyncio
import asyncio


def get_agent_observations(state: AgentState):
    '''AdaptiveContextManagement: The context behind the current state s_t <- s_(t+1) is analyzed and semantic representation of the context is provided in the prompts.
                                system_prompts: prompts are dynamically generated using WiSER's ContextManager's prompt_generator method
                                current_state: stores information on channel condition and impact factors for every state 
        return: agent_observations in the form of prompts.
    '''        
    acm = AdaptiveContextManagement(n_sta, n_ru, n_ap,  state.timestep)
    current_state, system_prompts = acm.prompt_generator(state.current_observations, state.env_feedback, json_schema_for_SRA, state.strategy_pool)
            
    state.agent_observations = {"current_state":current_state, "system_prompts":system_prompts}
    return {"agent_observations": state.agent_observations}
    

async def async_xLMCall(scheduler, client, model, agent_observations):
    
    tasks = [scheduler.xlm_scheduler(client, model, prompt) for prompt in agent_observations]
    schedule = await asyncio.gather(*tasks)

    return schedule

def call_scheduler(state: AgentState):
    '''scheduling_engine: Implements different wireless user scheduling methods (best channel quality-based scheduler, random scheduler, xLM-optimized scheduler).
                        random/BCQ-based schedulers: schedules users/STAs randomly/based on highest channel gains for the given state of the wireless network.
                        MAxLM schedulers: adopts the multi-agent framework to asynchronously call an xLM 
                        to perform SRA with the objective to either schedule users 
                        with the highest channel gains or maximize the UL throughput. 
        ModelOutputParser: Implements methods to effectively parse the xLM's SRA intent (i.e., xLM response)'
        return: agent_schedule with the resource assignments for the given state
    '''  
    scheduler = scheduling_engine(n_sta, n_ru, n_ap) 
    
    if (state.timestep ==0) or intent_based_strategy == 2:
        #actions = scheduler.random_actions() # assigns RUs randomly
        actions = scheduler.BCQ_scheduler(state.agent_observations["current_state"]["channel_gains"])
        flag_responseFails = np.array(np.zeros((1,n_sta)))
        
    else:

        parse = ModelOutputParser(n_sta, n_ru, n_ap, model_filename[model], prompt_template, try_num, strategy_pool["SRA_Algo"][intent_based_strategy])
        for retry in range(3):
            if state.timestep == 1:
                print("Loading xLM: ",model_filename[model],", to perform UL SRA based on the user intent: ", strategy_pool["SRA_Algo"][intent_based_strategy])
            loop = asyncio.get_event_loop()
            xlm_schedule = loop.run_until_complete(async_xLMCall(scheduler, client, wiser_models[model], state.agent_observations["system_prompts"]))
            
            actions, flag_responseFails, fail_count = parse.xLM_intent(xlm_schedule) 
            if len(fail_count) == 0:
                break
            else:
                print("Calling xLM again to perform SRA for timestep,", ts)
        
    state.agent_schedule = {"actions":actions, "flag_responseFails": flag_responseFails}
    return {"agent_schedule": state.agent_schedule, "agent_observations": state.agent_observations}


def scheduled_transmission(state: AgentState):
    '''EnvironmentManager: Implements methods to render wireless network environment 
                        by connecting to external engines (currently utlizes MATLAB engine to simulate UL-SA).
        return: env_feedback containing feedback characterizing the result of the scheduling/RU assignments.
    '''  
    
    impact_factors = state.agent_observations["current_state"]["impact_factors"]
    
    wlan = EnvironmentManager(n_sta, n_ru, n_ap, state.timestep)
    feedback = wlan.access_point_terminal(state.current_observations, state.agent_schedule, impact_factors, eng) 
    
    state.env_feedback["ratesN"] = feedback["ratesN"]
    state.env_feedback["original_actions"] = feedback["current_actions"]
    state.env_feedback["flag_responseFails"] = feedback["flag_responseFails"]
    state.env_feedback["final_actions"] = feedback["final_actions"]
    violation_count = np.sum(feedback["violations"])
    if violation_count > 0 and state.timestep > 0:
        violations_perEpi[state.episode, state.timestep] = 1

    return {"env_feedback":state.env_feedback}


if __name__ == '__main__':
    
    """ AI-assisted Wireless Systems Engineering and Research (WiSER) facilitates autonomous 
    wireless user scheduling and resource management (SRA) of MU-MIMO-OFDMA-enabled WLAN or 5G/6G networks
    
    In particular, WiSER models the SRA tasks for a given state of the dynamic wireless network environment 
    as a Markov Decision Process (MDP) problem and defines the MDP componenets: agent, agent's state space, action space, and feedback from the environment.
    
    In terms of system design, the MDP componenents and performing SRA for a given state of the network is implemented using the graphs.
    The graph consists of the following graph nodes.
    Node 1: get_agent_observations(current_state_of_network_environment)
            Args: 
                current_state: contains a dictionary with information on channel gains and spatial compatibility among the STAs to charactierize the AP-STA connections
                system_prompts: contain prompts characterizing the varying context of dynamically changing network environment.
                returns: agent_observations
    Node 2: call_scheduler(prompts)
            Args:
                system_prompts: prompts for the xLM to perform SRA based on user's SRA intent.
                returns: agent_schedule
                
    Node 3: schedule_transmission(RU_assignments)
            Args:
                agent_schedule: contains the resource assignments to initiate Uplink Scheduled Access (UL-SA).
                returns: Feedback from the wireless network environment (original RU assignments, MIMO spaital constraint violations, Revised RU assignments, UL throughput, xLM parsing error)
    The WiSER's graph is built using LangGraphs's Graph API and requires adhering to the following instructions from LanGraph.
    **`StateGraph` is a builder class and cannot be used directly for execution.
    You must first call `.compile()` to create an executable graph that supports
    methods like `invoke()`, `stream()`, `astream()`, and `ainvoke()`. See the
    `CompiledStateGraph` documentation for more details.
    
    Example:
        ```python
        #Load WiSER modules--------
        from Context_Manager import AdaptiveContextManagement
        from Environment_Manager import EnvironmentManager
        from langgraph.graph import START, END, StateGraph
        from wiser_state_schema import (
            AgentState, 
            StateInput, 
            StateOutput,
            )
        
        get_agent_observations(state:AgentState):
            return agent_observations
        call_scheduler(state:AgentState):
            return agent_schedule
        schedule_transmission(state:AgentState):
            return env_feedback
        
        Build WiSER graph
        wiser_graph = StateGraph(AgentState, input_schema= StateInput , output_schema= StateOutput)
        wiser_graph.add_node("get_agent_observations", get_agent_observations)
        wiser_graph.add_node("call_scheduler", call_scheduler)
        wiser_graph.add_node("scheduled_transmission", scheduled_transmission) 
        
        compiledWiSERGraph = wiser_graph.compile()
        for e =1:E episodice interaction with the WLAN environment do:
            for ts=1:50 time-slotted UL-SA do:
                trigger_ULSA = StateInput(
                    current_observations = current_ts, 
                    env_feedback=env_feedback, 
                    strategy_pool = strategy_pool, timestep = 0, episode= i)
                
                # Inititate UL-SA --------------------------------------
                state_feedBacks = compiledWiSERGraph.invoke(trigger_ULSA)
        File Manager records UL rate-sum, feedback, xLM SRA intent, 
        parsing errors, MIMO spatial constraint violations, plots CDF of rate-sum for 50 UL-SA in test episodes.        
    """
    
    #WLAN Parameters-------------------------
    n_sta = 10
    n_ap = 4
    n_ru = 9
    
    # xLM selection 
    wiser_models = ["mistral-nemo:latest","llama3.1:8b","gemma3:12b"]
    model_filename = ["mistral-nemo12b","llama8b","gemma12b"]
    model = 0
    # Details to save outcome as files using the File Manager
    prompt_template = "_pt1_"  # Specific title for each prompt templates
    try_num = 1                     # Every file name includes the number of runs made with each prompt template or experiments
    
    # Intent-based Strategies -----------------------------------------------
    intent_based_strategy = 1
    strategy_pool = {"intent":intent_based_strategy,"strategy":[BCQ, MAxLM], "SRA_Algo":["_MAxLM_performing_BCQ-based_SRA_", "_MAxLM-optimized_SRA_", "_BCQ-based_SRA_"]}
    print("Intent-based strategy to manage the network: ",strategy_pool["SRA_Algo"][intent_based_strategy])
    
    # File Manager loads WLAN channel data for 1200 episodes
    print("File manager retrieving the collected WLAN channel data to simulate UL-SA and perform UL SRA....")
    fileManager = FileManager(model_filename[model], prompt_template, try_num, strategy_pool["SRA_Algo"][intent_based_strategy])
    wlan_data = fileManager.loadChanneldata(n_sta, n_ap)
    wlan_observations = (np.char.replace(wlan_data, 'i', 'j').astype(complex))
    print("Retrieval complete! WLAN channel data loaded for 1200 episodes.")
    
    # Randomly selected 5 episodes:Test-time inference data set only =================================================================================999999999999999999999999999999999999999999999999999999999999999
    test_set = np.array([[5, 1200, 1100, 1080, 1025, 1140]])
    # Test Episode's parameters
    # There are 51 time-slotted UL-SA in each test episode. 
    #The first time-slot represents the initial state, s_o and is used to begin the MAxLM-optimized SRA
    max_timesteps = 51
    max_episodes =  np.size(test_set)  

    # Parameters to gauge/monitor performance
    # Revised RU assignments for every time-slotted UL-SA is stored here for all episodes
    actions_perEpi = np.array(np.zeros((max_episodes,(max_timesteps*(n_sta*n_ru)))))
    # Original RU assignments for every time-slotted UL-SA is stored here for all episodes
    orig_actions_perEpi = np.array(np.zeros((max_episodes,((max_timesteps)*(n_sta*n_ru)))))
    # Flags to record MIMO spatial contraint violations and failed attempts to parse LLM responses
    violations_perEpi = np.array(np.zeros((max_episodes,(max_timesteps))))
    xlm_parseError = np.array(np.zeros((max_episodes,((max_timesteps)*n_sta))))
    
    # LangGraph's StateGraph is defined below for WiSER---------------------
    # AgentState and the input/output shared state schema is defined in wiser_state script
    wiser_graph = StateGraph(AgentState, input_schema= StateInput , output_schema= StateOutput)
    # Wiser graph nodes and edges -------------------------------------------
    wiser_graph.add_node("get_agent_observations", get_agent_observations)
    wiser_graph.add_node("call_scheduler", call_scheduler)
    wiser_graph.add_node("scheduled_transmission", scheduled_transmission)    
    # Sequential connections enabled by edges
    wiser_graph.add_edge(START,"get_agent_observations")
    wiser_graph.add_edge("get_agent_observations", "call_scheduler")
    wiser_graph.add_edge("call_scheduler", "scheduled_transmission")
    wiser_graph.add_edge("scheduled_transmission", END)
    # Compile WiSER StateGraph to invoke later-------------------------------
    compiledWiSERGraph = wiser_graph.compile()
    print("Initiating WiSER and MATLAb engine....")
    # Start MATLAB engine and open ports for asynchronous connection with client
    eng = matlab.engine.start_matlab()
    nest_asyncio.apply()
    client = AsyncClient() #instantiate async client
    
    # Start SRA for the test episodes
    for i in range(max_episodes):
        # Load test episode from the randomly selected episodes in test_set -------------------
        test_episode = int(test_set[0,i])
        # Extract the WLAN data for the selected test episode------------------
        set_end = int( (test_set[0,i]*(max_timesteps-1)) )  
        set_start = int( (test_set[0,i]*(max_timesteps-1)) - (max_timesteps+1) ) # -1 because WLAN obs data is 1 bigger then max timestep due to next state computations
        obsEpi = wlan_observations[set_start:set_end,:]    
        print("Starting SRA based on user intent, for the 50 UL-SA in the randomply selected test episode ", test_episode)
        
        # Initialize variables for UL-SA: UL-SA rate-sum, feedback from WLAN environment (currently only the xLM parsing error is utilized in the prompts)
        rate_ts = np.array(np.zeros(((max_timesteps),1))) # this will inlcude the rate-sum for the initial state
        # feedback from environment contains information on xLM parsing error and the rest is for plot/analysis/files
        env_feedback = {"ratesN": np.array(np.zeros((1,n_sta))), "final_actions": np.array(np.zeros((n_sta,n_ru))), "original_actions": np.array(np.zeros((n_sta,n_ru))), "flag_responseFails":np.array(np.zeros((1,n_sta))), "violation_count":0, "timestep":[]}
    
        # information on s_t and s_(t+1) passed on for dynamic prompt generation
        current_ts = obsEpi[0,:].reshape(1,len(obsEpi[0,:]))
        trigger_ULSA = StateInput(
            current_observations = current_ts, 
            env_feedback=env_feedback, 
            strategy_pool = strategy_pool, timestep = 0, episode= i)
        
        # Inititate t=0 UL-SA --------------------------------------
        state_feedBacks = compiledWiSERGraph.invoke(trigger_ULSA)
        # Storing feedback for the initial state of the WLAN env and UL-SA
        env_feedback = state_feedBacks["env_feedback"]
        rate_ts[0,:] = np.sum(env_feedback["ratesN"])
        
        
        for ts in range(1,max_timesteps):
            
            # Loading channel/SNR/noise data to generate prompts for t=ts and t =ts+1, which are s_t and s_(t+1)-------------------------
            current_ts = obsEpi[ts,:].reshape(1,len(obsEpi[ts,:]))
            trigger_ULSA = StateInput(current_observations = current_ts, 
                                      env_feedback= env_feedback, 
                                      strategy_pool = strategy_pool, timestep = ts, episode= i)
            
            state_feedBacks = compiledWiSERGraph.invoke(trigger_ULSA)
            env_feedback = state_feedBacks["env_feedback"]
            if ts == 2:
                print("Approximately 20-30 mins to perform SRA for all 50 UL-SA in test episodes. CDF of the rate-sum will be plotted upon completion.")
            rate_ts[ts,:] = np.sum(env_feedback["ratesN"])
            actions_perEpi[i,(ts*(n_sta*n_ru)):((ts+1)*(n_sta*n_ru))] = env_feedback["final_actions"].reshape(1,(n_sta*n_ru))
            orig_actions_perEpi[i,(ts*(n_sta*n_ru)):((ts+1)*(n_sta*n_ru))] = env_feedback["original_actions"].reshape(1,(n_sta*n_ru))
            xlm_parseError[i,(ts*n_sta):((ts+1)*n_sta)] = env_feedback["flag_responseFails"]
            print(f"SRA performed for timestep: {ts}", end="\r", flush=True)
    
        # Save action indices per episode--------------------------------
        actions_allAgent_echEpi = np.array(actions_perEpi, dtype ='str')
        typeA_t = 1 # revised Actions
        fileManager.save_RUAssignments(actions_allAgent_echEpi, typeA_t)
        
        
        # Save original action indices per episode--------------------------------
        orig_actions_allAgent_echEpi = np.array(orig_actions_perEpi, dtype ='str')
        typeA_t = 0 #Original Actions
        fileManager.save_RUAssignments(orig_actions_allAgent_echEpi, typeA_t)
        
        #Record xLM parsing Errors during episodic interactions --------------
        parsingErrors_echEpi = np.array(xlm_parseError, dtype ='str')
        fileManager.record_ParsingErrors(parsingErrors_echEpi)
        
        # Record violation of the MIMO user grouping constraint
        violations_allAgent_echEpi = np.array(violations_perEpi, dtype ='str')
        fileManager.record_spatialConstraint_violations(violations_allAgent_echEpi) 
        
        # Plot the CDF of UL rate-sum achieved during each of the 50 UL-SA in the test episode and save the rates
        violationT = np.sum(violations_perEpi[i,:])
        fileManager.cdf_RateSum(violationT, rate_ts, max_timesteps, test_episode, intent_based_strategy)
        





