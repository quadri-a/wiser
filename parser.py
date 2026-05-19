import numpy as np
import re
from pydantic import BaseModel, Field
from File_Manager import FileManager

class UserInfo(BaseModel):
    resource_allocation_array: list[int] = Field(description="Resource allocation array")
    reasoning: str = Field(description="This field contains any step-wise analysis of agent's state and the reasoning behind the the resource allocation strategy.") 


class ModelOutputParser():
    def __init__(self, n_sta, n_ru, n_ap, model_name, prompt_template, try_num, strategy_desc):
        self.n_sta = n_sta
        self.n_ru = n_ru
        self.n_ap = n_ap
        self.scheduler = model_name
        self.pt = prompt_template
        self.experiment = try_num
        self.strategy = strategy_desc
    
    
    def extract_processed_response(self, text):
        """
        Parameters
        ----------
        text : str
            contains xLM's SRA intent as the following JSON formatted output:
                {"resource_allocation_array":[] 
                 "reasoning":""}
        Returns
        -------
        flattened_content : Extracts the resource assignments and strategy from the JSON format.

        """
        # Regex pattern to find content between ``` and ```
        # The '?' makes it non-greedy, stopping at the first closing ```
        # The 's' flag (re.DOTALL) allows '.' to match newlines
        pattern = r"```.*?```"
        # Find all occurrences of the pattern
        matches = re.findall(pattern, text, re.DOTALL)
        if len(matches) == 0:
            pattern = r"\{[^{}]*\}"
            matches = re.findall(pattern, text, re.DOTALL)
        flattened_content = {}
        for match in matches:
            # Remove the triple backticks from the start and end of the match
            content = match.strip('`')
            # Remove any leading/trailing whitespace including newlines
            content = content.strip()
            content = content.strip('json')
            # Remove all newline characters within the content
            flattened_content = content.replace('\n', '').replace('\r', '')
            #processed_matches.append(flattened_content)
        return flattened_content
    
    
    def xLM_intent(self, xlm_response):
        """
        Parameters
        ----------
        xlm_response : json instance
           contains the JSON formatted output with the xLM's SRA intent and resoning behind the intent.

        Returns
        -------
        actions : int
            a NxR matrix containing the binary RU assignments/schedule for the t^th UL-SA.
        flag_responseFails : int
            a 1xN array containing the flags indicating possible types of parsing errors that may result from attempting to parse the xLM's SRA intent.
        failed_agents : int
            an array populated with the agents for which xLM's SRA intent could not be parsed.
            essenstially keeps count of parsing errors.
        """
        actions = np.array(np.zeros((self.n_sta,self.n_ru)))
        flag_responseFails = np.array(np.zeros((1,self.n_sta)))
        failed_agents = []
        fileManager = FileManager(self.scheduler, self.pt, self.experiment, self.strategy)
        for i, schedule in enumerate(xlm_response):
            try:
                agent_info = UserInfo.model_validate_json(schedule)
                resources = agent_info.resource_allocation_array
                if len(resources) > 0:
                    for ru in range(len(resources)):
                        if resources[ru] > self.n_ru or resources[ru] < 1:
                            actions[i,:] = np.array(np.zeros((1,self.n_ru)))
                            print("xLM Response contains the invalid RU index in ", resources ," for RU ", ru, ". Nullifying RA ...")
                            break
                        else:   
                            actions[i,(resources[ru]-1)] = 1
                if len(actions[i,:]) > self.n_ru:
                    print("Parsed JSON output. But action array is longer. Nullifying RA ...")
                    actions[i,:] = np.array(np.zeros((1,self.n_ru)))
                    flag_responseFails[:,i] = 1
                    failed_agents.append(i)
                    fileManager.write_xlm_response(schedule, flag_responseFails[:,i] )
                ac = actions[i,:]
                if np.sum(actions[i,:]) > self.n_ru or np.sum(actions[i,:]) < 0 or len(ac[ac>1])>0 or len(ac[ac<0]) > 0:
                    print("Parsed Output. But array contains invalid index (non-binary). Nullifying RA ...")
                    actions[i,:] = np.array(np.zeros((1,self.n_ru)))
                    flag_responseFails[:,i] = 2
                    failed_agents.append(i)
                    fileManager.write_xlm_response(schedule, flag_responseFails[:,i] )
    
            except ValueError:
                json_string = self.extract_processed_response(schedule)
                try:
                    agent_info = UserInfo.model_validate_json(json_string)
                    resources = agent_info.resource_allocation_array
                    if len(resources) > 0:
                        for ru in range(len(resources)):
                            if resources[ru] > self.n_ru or resources[ru] < 1:
                                actions[i,:] = np.array(np.zeros((1,self.n_ru)))
                                print("xLM Response contains the invalid RU index in ", resources ," for RU ", ru, ". Nullifying RA ...")
                                break
                            else:   
                                actions[i,(resources[ru]-1)] = 1
                    if len(actions[i,:]) > self.n_ru:
                        print("Parsed JSON output. But action array is longer. Nullifying RA ...")
                        actions[i,:] = np.array(np.zeros((1,self.n_ru)))
                        flag_responseFails[:,i] = 1
                        failed_agents.append(i)
                        fileManager.write_xlm_response(schedule, flag_responseFails[:,i] )
                    ac = actions[i,:]
                    if np.sum(actions[i,:]) > self.n_ru or np.sum(actions[i,:]) < 0 or len(ac[ac>1])>0 or len(ac[ac<0]) > 0:
                        print("Parsed Output. But array contains invalid index (non-binary). Nullifying RA ...")                      
                        actions[i,:] = np.array(np.zeros((1,self.n_ru)))
                        flag_responseFails[:,i] = 2
                        failed_agents.append(i)
                        fileManager.write_xlm_response(schedule, flag_responseFails[:,i] )
    
                except ValueError:
                    actions[i,:] = np.array(np.zeros((1,self.n_ru)))
                    flag_responseFails[:,i] = 1 
                    failed_agents.append(i)
                    fileManager.write_xlm_response(schedule, flag_responseFails[:,i] )
                    print("\n Could not parse response for Agent ", i)
        
        return actions, flag_responseFails, failed_agents
