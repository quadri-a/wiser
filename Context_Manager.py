import numpy as np
from numpy import linalg as LA

from wiser_modular_prompts import (
    role_task_BCQ,
    role_task_MAxLM,
    parsing_instructions,
    parser_error,
    parser_error_out_of_Range,
    strategy_response_format
    )

class AdaptiveContextManagement:
    def __init__(self, n_sta, n_ru, n_ap, ts):
        self.n_sta = n_sta
        self.n_ru = n_ru
        self.n_ap = n_ap
        self.ts = ts
    
    def MAxLM_SRA_pt1(self, SNR, impact_factors, flag_responseFails, json_schema, strategy_pool, ts):
        """
        Parameters
        ----------
        chnGain : float
            NxR matrix contianing the channel gains of the N agents (AP-STA UL connections).
        flag_responseFails : int
            1xN dimensional array containing information on xLM parsing error by flagging different typesof possible parsing errors.
        json_schema : str
            contains instructions informating the xLM on how to format the SRA intent for the t^th UL-SA.
        strategy_pool : dict
            contains information on user's intent for SRA.
        ts : int
           t^th state of the wlan environment/t^th UL-SA for which the SRA is performed.

        Returns
        -------
        system_prompts : str
            contains the N prompts for the xLM to perform SRA for the t^th UL-SA.
        
        Objective: 
            Generate prompts to enable the xLM to intelligently assign resources to maximize UL throughput.
        Method: 
            Uses prompt template 1 to provide sementic analysis of agent's attributes: channel strength, spatial compatibility, and comparison of agent's attributes with that of the others.
        """
        n_sta = self.n_sta
        n_ru = self.n_ru
        g_s = self.n_ap
        system_prompts = []
        
        for agent in range(n_sta):
            agent_attributes = []
    
            for ru in range(n_ru):
                agent_strength = [] 
                agent_compatibility = []
                
                sorted_gains = np.argsort(SNR[:,ru])
                sorted_impacts = np.argsort(impact_factors[:,ru])
                
                strength_index = np.where(sorted_gains == agent)
                impact_index = np.where(sorted_impacts == agent)
                
                g_s_strongest = sorted_gains[int(strength_index[0]+1):]
                most_strongest = sorted_gains[int(n_sta-len(g_s_strongest)):]
                most_compatible = sorted_impacts[int(n_sta-len(g_s_strongest)):]
                if len(most_compatible) > len(most_strongest):
                    big_list = most_compatible
                    small_list = most_strongest
                else:
                   big_list = most_strongest
                   small_list = most_compatible

                list_commons = []
                for d in range(len(small_list)):
                    for l in range(len(big_list)):
                        if small_list[d] == big_list[l]:
                            list_commons.append(small_list[d])

                list_commons = np.array(list_commons)
                
                if strength_index[0] == (n_sta-1):
                    strength = "- Agent"+str(agent+1)+" is the strongest!\n"
                elif strength_index[0] == 0:
                    strength = "- Agent"+str(agent+1)+" is the weakest!\n"
                elif (n_sta - strength_index[0]) <= g_s:
                    strength = "- Agent"+str(agent+1)+" is one of the "+str(g_s)+" strongest agents.\n" 
                else:
                    strength = "- Agent"+str(agent+1)+" is NOT one of the "+str(g_s)+" strongest agents.\n"
                
                agent_strength.append(strength)
                
                if impact_index[0] == 0:
                    impact = "- Agent"+str(agent+1)+" is incompatible with all the agents! \n"
                elif impact_index[0] == (n_sta-1):
                    if len(list_commons) == 0:
                        impact = "- Agent"+str(agent+1)+" is the most compatible agents! \n"
                    else:
                        better_agents = len(list_commons)
                        if better_agents >= g_s:
                            impact = "- Agent"+str(agent+1)+" is the most compatible agents. \n- However, there are "+str(g_s) +" other agents stronger than Agent"+str(agent+1)+" that are also compatible with others, and are likely to share RU"+str(ru+1)+".\n- Note, only an optimal group of "+str(g_s)+" agents can share the same resource.\n"
                        else:
                            impact = "- Agent"+str(agent+1)+" is one of the "+str(g_s)+" most compatible agents.\n- But, there are also "+str(better_agents) +" other agents stronger than Agent"+str(agent+1)+" that are also compatible with others. \n"     
                elif (n_sta - impact_index[0])<=g_s:
                    
                    if len(list_commons) == 0:    
                        impact = "- Agent"+str(agent+1)+" is one of the "+str(g_s)+" most compatible agents.\n"
                    else:
                        better_agents = len(list_commons)
                        if better_agents >= g_s:
                            impact = "- Agent"+str(agent+1)+" is one of the "+str(g_s)+" most compatible agents.\n- However, there are "+str(g_s) +" other agents stronger and more compatible than Agent"+str(agent+1)+" that are likely to share RU"+str(ru+1)+".\n- Note, only an optimal group of "+str(g_s)+" agents can share the same resource.\n"
                        else:
                            impact = "- Agent"+str(agent+1)+" is one of the "+str(g_s)+" most compatible agents.\n- But, there are also "+str(better_agents) +" other agents that are both stronger and more compatible than Agent"+str(agent+1)+". \n"       
                else:
                    impact = "- Agent"+str(agent+1)+" is NOT one of the "+str(g_s)+" most compatible agents.\n"\
                    
                agent_compatibility.append(impact)
                
                resource = "Over resource RU"+str(ru+1)+ ", compared to the "+str(n_sta-1)+" agents: \n"
                assignment = "Based on Agent"+str(agent+1)+"'s current condition compared to others over RU"+str(ru+1)+", decide if the resource RU"+str(ru+1)+" should be assigned to Agent"+str(agent+1)+"?\n"
                ru_strengths_impacts = resource + ''.join(agent_strength) + ''.join(agent_compatibility) + assignment
                
                agent_attributes.append(ru_strengths_impacts)
        
                ibs_strategy0 = strategy_pool["strategy"][1]
                max_agent= {"g_s":g_s, "i":(agent+1)} 
                agent_strategy = (ibs_strategy0).format(**max_agent)
               
            prompt_parameters = {"n_sta": n_sta,"n_sta-1": (n_sta-1), 
                               "n_ru": n_ru, "n_ap": g_s, "i": (agent+1), 
                               "ts":self.ts, 
                               "strategy": agent_strategy, }
            
            system_prompt_eager = role_task_MAxLM.format(**prompt_parameters)+ "\n" + '\n'.join(agent_attributes) +"\n" + strategy_response_format.format(**prompt_parameters) + "\n"
            
            if flag_responseFails[:,agent] == 1:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n' + parser_error.format(**prompt_parameters)
            elif flag_responseFails[:,agent] == 2:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n' + parser_error_out_of_Range.format(**prompt_parameters)
            else:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n'
            
            system_prompts.append(system_prompt)
        
        return system_prompts
    
    def BCQ_SRA_pt2(self, chnGain, flag_responseFails, json_schema, strategy_pool, ts):
        """
        Parameters
        ----------
        chnGain : float
            NxR matrix contianing the channel gains of the N agents (AP-STA UL connections).
        flag_responseFails : int
            1xN dimensional array containing information on xLM parsing error by flagging different typesof possible parsing errors.
        json_schema : str
            contains instructions informating the xLM on how to format the SRA intent for the t^th UL-SA.
        strategy_pool : dict
            contains information on user's intent for SRA.
        ts : int
           t^th state of the wlan environment/t^th UL-SA for which the SRA is performed.

        Returns
        -------
        system_prompts : str
            contains the N prompts for the xLM to perform SRA for the t^th UL-SA.
        
        Objective: 
            Generate prompts to enable the xLM to assign resources to STAs with the highest channel gains over each of the nine RUs.
        Method: 
            Uses prompt template 2 to provide numeric analysis of agent's attributes: channel strength.
        """
        n_sta = self.n_sta
        n_ru = self.n_ru
        g_s = self.n_ap
        system_prompts = []
        
        for agent in range(n_sta):
            agent_attributes = []
    
            for ru in range(n_ru):
                agent_strength = []            
                strength = "".join(str(chnGain[:,ru])).replace('[[','').replace(']]','').replace('\n','')
                resource = "Over resource RU"+str(ru+1)+ ", the following array contains the information on Agent1 to Agent"+str(n_sta)+"'s strength:"+strength +". \n"
                agent_strength.append(resource)
                
                assignment = "Is Agent"+str(agent+1)+" one of the "+str(g_s)+" strongest agents over RU"+str(ru+1)+"?\n Strictly follow the resource allocation strategy to determine the assignment of resource RU"+str(ru+1)+" to Agent"+str(agent+1)+".\n"
            
                ru_strengths_impacts = ''.join(agent_strength) + assignment
                agent_attributes.append(ru_strengths_impacts)
        
                ibs_strategy0 = strategy_pool["strategy"][0]
                max_agent= {"g_s":g_s, "i":(agent+1)} 
                agent_strategy = (ibs_strategy0).format(**max_agent)
               
            prompt_parameters = {"n_sta": n_sta,"n_sta-1": (n_sta-1), 
                               "n_ru": n_ru, "n_ap": g_s, "i": (agent+1), 
                               "ts":self.ts, 
                               "strategy": agent_strategy, }
            
            system_prompt_eager = role_task_BCQ.format(**prompt_parameters)+ "\n" + '\n'.join(agent_attributes) +"\n" + strategy_response_format.format(**prompt_parameters) + "\n"
            
            if flag_responseFails[:,agent] == 1:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n' + parser_error.format(**prompt_parameters)
            elif flag_responseFails[:,agent] == 2:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n' + parser_error_out_of_Range.format(**prompt_parameters)
            else:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n'
            
            system_prompts.append(system_prompt)
        
        return system_prompts

    def BCQ_SRA_pt1(self, chnGain, flag_responseFails, json_schema, strategy_pool, ts):
        """
        Parameters
        ----------
        chnGain : float
            NxR matrix contianing the channel gains of the N agents (AP-STA UL connections).
        flag_responseFails : int
            1xN dimensional array containing information on xLM parsing error by flagging different typesof possible parsing errors.
        json_schema : str
            contains instructions informating the xLM on how to format the SRA intent for the t^th UL-SA.
        strategy_pool : dict
            contains information on user's intent for SRA.
        ts : int
           t^th state of the wlan environment/t^th UL-SA for which the SRA is performed.

        Returns
        -------
        system_prompts : str
            contains the N prompts for the xLM to perform SRA for the t^th UL-SA.
        
        Objective: 
            Generate prompts to enable the xLM to assign resources to STAs with the highest channel gains over each of the nine RUs.
        Method: 
            Uses prompt template 1 to provide sementic analysis of agent's attributes: channel strength.
        """
        n_sta = self.n_sta
        n_ru = self.n_ru
        g_s = self.n_ap
        system_prompts = []
        
        for agent in range(n_sta):
            agent_attributes = []
    
            for ru in range(n_ru):
                agent_strength = []            
                sorted_gains = np.argsort(chnGain[:,ru])
                strength_index = np.where(sorted_gains == agent)
        
                if (n_sta - strength_index[0]) <= g_s:
                    strength = "- Agent"+str(agent+1)+" is one of the "+str(g_s)+" strongest agents!\n"
                else:
                    strength = "- Agent"+str(agent+1)+" is NOT one of the "+str(g_s)+" strongest agents.\n"
                agent_strength.append(strength)
                
                resource = "Over resource RU"+str(ru+1)+ ", compared to the "+str(n_sta-1)+" agents: \n"
                assignment = "Strictly follow the resource allocation strategy to determine the assignment of resource RU"+str(ru+1)+" to Agent"+str(agent+1)+".\n"        
                ru_strengths_impacts = resource + ''.join(agent_strength) + assignment
                
                agent_attributes.append(ru_strengths_impacts)
        
                ibs_strategy0 = strategy_pool["strategy"][0]
                max_agent= {"g_s":g_s, "i":(agent+1)} 
                agent_strategy = (ibs_strategy0).format(**max_agent)
               
            prompt_parameters = {"n_sta": n_sta,"n_sta-1": (n_sta-1), 
                               "n_ru": n_ru, "n_ap": g_s, "i": (agent+1), 
                               "ts":self.ts, 
                               "strategy": agent_strategy, }
            
            system_prompt_eager = role_task_BCQ.format(**prompt_parameters)+ "\n" + '\n'.join(agent_attributes) +"\n" + strategy_response_format.format(**prompt_parameters) + "\n"
            
            if flag_responseFails[:,agent] == 1:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n' + parser_error.format(**prompt_parameters)
            elif flag_responseFails[:,agent] == 2:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n' + parser_error_out_of_Range.format(**prompt_parameters)
            else:
                system_prompt = system_prompt_eager + parsing_instructions.format(**prompt_parameters) + '\n' + json_schema.format() + '\n'
            
            system_prompts.append(system_prompt)
        
        return system_prompts
    
    def prompt_generator(self, current_info, feedback, json_schema, strategy_pool):
        """
        Parameters
        ----------
        current_info : float
            contains information on AP-STA channel conditions (NxR), SNR (NxR), noise (1xR)
        feedback : dict
            contains feedback from agent's environment.
        json_schema : str
            contains instructions informating the xLM on how to format the SRA intent for the t^th UL-SA.
        strategy_pool : dict
            contains information on user's intent for SRA.

        Returns
        -------
        current_state : float
            contains information on channel gains (NxR), spatial compatibility among the STAs as impact factors (NxR) among other things.
        system_prompts : str
            contains the N prompts for the xLM to perform SRA for the t^th UL-SA.

        """
        
        n_ru = self.n_ru
        n_sta = self.n_sta
        n_ap = self.n_ap
        ts = self.ts
        per_RUData = (n_ap*n_sta)
        user_SNRData = (n_ap*n_sta*n_ru) + (n_ap*n_sta)
        current_state = []
        
        flag_responseFails = np.array(feedback["flag_responseFails"])
    
        #Declare variables---------------------------
        chnGain= np.array(np.zeros((n_sta,n_ru)), dtype = 'float32')
        origSNR = np.array(np.zeros((n_sta,n_ru)), dtype = 'float32')
        
        # Channel gain of N STAs on all R RUs -----------------------------------------------------------------------------------
        for ru in range(n_ru):
            users_chnData = current_info[:,(ru*per_RUData):((ru+1)*per_RUData)]
            users_snrData = current_info[:, (user_SNRData+(ru*n_sta) ): (user_SNRData+((ru+1)*n_sta) ) ]
            for k in range(n_sta):
                chnGain[k,ru] = (LA.norm(10*(users_chnData[:, (k*n_ap):((k+1)*n_ap)]))**2)
                origSNR[k,ru] = np.real(users_snrData[:,k]) 
        
        sta_impact = np.array(np.zeros((n_sta,n_ru)), dtype ='float32')
        impact_factors = np.array(np.zeros((n_sta,n_ru)), dtype ='float32')
    
        for i in range(n_sta):
            norm_gain = []
            norm_chns = chnGain/chnGain[i,:]
    
            for j in range(n_sta):
                if i != j:
                    norm_gain.append(norm_chns[j,:])
            norm_gain = np.array(norm_gain, dtype = 'float32')
    
            sta_impact[i,:] = np.mean(norm_gain,0)
            impact_factors[i,:] = sta_impact[i,:]/(np.mean(sta_impact[i,:]))
            
        current_state = {"channel_gains": chnGain, "SNR":origSNR, "impact_factors": impact_factors, "ts":ts}
        if strategy_pool["intent"] == 0:
            system_prompts = self.BCQ_SRA_pt1(chnGain, flag_responseFails, json_schema, strategy_pool, ts)
            #system_prompts = self.BCQ_SRA_pt2(chnGain, flag_responseFails, json_schema, strategy_pool, ts)
        else:
            system_prompts = self.MAxLM_SRA_pt1(chnGain, impact_factors, flag_responseFails, json_schema, strategy_pool, ts)
            
        return current_state, system_prompts
