from dataclasses import dataclass, field

@dataclass
class AgentState:
    # During episodic interaction with the WLAN environment these parameters are generally required for every scheduled transmission in an episode
    max_timesteps: float = field(default=None)
    max_episodes: float = field(default=None)
    timestep: int = field(default=None)
    episode: int=field(default=None)
    # Network Parameters
    n_sta: int = field(default=None)
    n_ru: int = field(default=None)
    n_ap: int = field(default=None)
    current_observations: float = field(default=None)
    #Agent 
    agent_observations: dict = field(default=None)
    agent_schedule: dict = field(default=None)
    #Feedback and IBS    
    env_feedback: float = field(default=None)
    strategy_pool: float = field(default=None)
    
@dataclass
class StateInput:
    # Typically, should include state observations parameters here but will only contain the user query to initiate LLM scheduling for the current state
    timestep: int = field(default=None)
    episode: int=field(default=None)
    strategy_pool: float = field(default=None)
    # WLAN config and data
    current_observations: float = field(default=None)
    #Feedback    
    env_feedback: float = field(default=None)
    
    
@dataclass 
class StateOutput:
    # Will be used to pass on the LLM's scheduling decision to the WLAN AP to initiate scheduled transmissions.
    env_feedback: float = field(default=None)
    











