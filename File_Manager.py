import os
import numpy as np
import matplotlib.pyplot as plt
import csv

class FileManager:
    def __init__(self, model_name, prompt_template, attempt_num, strategy_desc):
        self.current_dir = os.getcwd()
        self.scheduler = model_name
        self.pt = prompt_template
        self.experiment = attempt_num
        self.strategy = strategy_desc

        
    def loadChanneldata(self, N, M, E):
        """
        Parameters
        ----------
        N : number of wireless users/STAs
        M: number of antenna on the WLAN AP
        
        Returns
        -------
        wlan_data: contains AP-STA channel condition (1xNR), SNR (1xNR), noise at AP (1xM) among other things
        """
        
        if N == 10 and M == 4:
            
            channel_data = "WLAN_Channel_SNR_Noise_data_4antAP_episode"+str(E)+".csv"
        else:
            channel_data = "WLAN_Channel_SNR_Noise_data_8antAP_1200episodes_50ULSA.csv"
            
        wlan_data = np.loadtxt(self.current_dir+'/10_stations/channel_data/'+channel_data, delimiter=',', dtype=np.complex128)
        return wlan_data
        
    
    def save_RUAssignments(self, SRA_actions, flag):
        """
        Parameters
        ----------
        SRA_actions : int
            NxR binary matrix containing RU assignments.
        flag : int
            type determining original or revised RU assignments.
        Returns
        -------
        None.
        """
        if flag == 1:
            action_allAgent = open(self.current_dir+'/10_stations/files/'+str(self.scheduler)+'/revised_SRA_with_Model_'+str(self.scheduler)+'_template'+str(self.pt)+'_and_strategy_'+str(self.strategy)+'_for_expNum_'+str(self.experiment)+'_and5Episodes.csv', 'w', newline='')
        else:
            action_allAgent = open(self.current_dir+'/10_stations/files/'+str(self.scheduler)+'/original_SRA_with_Model_'+str(self.scheduler)+'_template'+str(self.pt)+'_and_strategy_'+str(self.strategy)+'_expNum_'+str(self.experiment)+'_and5Episodes.csv', 'w', newline='')
        
        with action_allAgent:
            writer = csv.writer(action_allAgent, delimiter =",",quoting=csv.QUOTE_MINIMAL)
            writer.writerows(SRA_actions)
            print('****** RU Assignments saved succesfully! ************ ') 

    def record_ParsingErrors(self, ParsingErrors):
        """
        Parameters
        ----------
        ParsingErrors : max_episodes x (max_timesteps*N) array
           xLM parsing errors for the 50 UL-SA in the five selected test episodes .
        Returns
        -------
        None.
        """
        xlmErrors_allAgent = open(self.current_dir+'/10_stations/files/'+str(self.scheduler)+'/xLMParsingErrors_for_Model_'+str(self.scheduler)+'_using_template'+str(self.pt)+'_and_strategy_'+str(self.strategy)+'_for_expNum_'+str(self.experiment)+'_and5Episodes.csv', 'w',newline='')
    
        with xlmErrors_allAgent:
            writer = csv.writer(xlmErrors_allAgent, delimiter =",",quoting=csv.QUOTE_MINIMAL)
            writer.writerows(ParsingErrors)  
            print('****** Parsing Errors recorded succesfully! ************ ') 
            
    def record_spatialConstraint_violations(self, violationFrequency):
        """
        Parameters
        ----------
        violationFrequency : int
            count of the number of times MIMO spatial constraint was violated due to xLM's RU assignments 
            for the 50 UL-SA in the five test episodes
        Returns
        -------
        None.
        """
        violations_allAgent = open(self.current_dir+'/10_stations/files/'+str(self.scheduler)+'/spatialConstraint_Violations_by_Model_'+str(self.scheduler)+'_using_template'+str(self.pt)+'_and_strategy_'+str(self.strategy)+'_for_expNum_'+str(self.experiment)+'_and5Episodes.csv', 'w',newline='')
    
        with violations_allAgent:
            writer = csv.writer(violations_allAgent, delimiter =",",quoting=csv.QUOTE_MINIMAL)
            writer.writerows(violationFrequency) 
            print('****** Spatial constraint violations recorded succesfully! ************ ') 
            

    def cdf_RateSum(self, beta, MAxLM_rates, T, E, intent):
        """
        Parameters
        ----------
        beta : int
            count of the number of times MIMO spatial constraint was violated due to RU assignments/scheduling by xLM.
        MAxLM_rates : int
            UL-SA rate-sum achieved by the xLM for the 50 UL-SAs in the test episodes
        T : int
            timestep/time-slotted UL-SA.
        E : int
            randomly selected test episode from the 1200 episode containing WLAN channel data.
        intent : int
            user's intent to distribute resource units. there are 3 strategies user may enforce

        Returns
        -------
        None.

        """
        
        print("SRA for the 50 UL-SA is now complete. Plotting CDF ...")
        BCQ2  = np.loadtxt(self.current_dir+'/10_stations/BCQ_SRA_Rates/Epi'+str(E)+'_N_2_4antAP_BCQ_SRA_sumRates.csv', delimiter=',', dtype=str)
        BCQ3  = np.loadtxt(self.current_dir+'/10_stations/BCQ_SRA_Rates/Epi'+str(E)+'_N_3_4antAP_BCQ_SRA_sumRates.csv', delimiter=',', dtype=str)
        BCQ4  = np.loadtxt(self.current_dir+'/10_stations/BCQ_SRA_Rates/Epi'+str(E)+'_N_4_4antAP_BCQ_SRA_sumRates.csv', delimiter=',', dtype=str)
        
        BCQ2 = np.array(BCQ2, dtype = 'float32')
        BCQ3 = np.array(BCQ3, dtype = 'float32')
        BCQ4 = np.array(BCQ4, dtype = 'float32')
        
        cdf_xlm = np.sort(MAxLM_rates[1:,0])
        cdfRates_2 = np.sort(BCQ2[1:])
        cdfRates_3 = np.sort(BCQ3[1:])
        cdfRates_4 = np.sort(BCQ4[1:])
        
        y = np.arange((T-1))/float((T-1))
        
        BCQ_SRA_forDiff_M = [cdfRates_2, cdfRates_3, cdfRates_4]
        BCQ_best = np.argmax([np.sum(cdfRates_2), np.sum(cdfRates_3), np.sum(cdfRates_4)])
        if intent == 0:
            error_perc = ((np.sum(cdf_xlm) - np.sum(cdfRates_4))/np.sum(cdfRates_4))*100
            print("Percentage difference in rate-sum due to assignment errors made by MAxLM performing BCQ-based SRA and the actual BCQ-based SRA, for the test episode %i is %f%%---" %(E, error_perc))
            print("For test episode %i MIMO user grouping constraint was violated  %f  times xxxxxx " %(E, beta))
            
        else:
            gain = ((np.sum(cdf_xlm) - np.sum(BCQ_SRA_forDiff_M[BCQ_best]))/np.sum(BCQ_SRA_forDiff_M[BCQ_best]))*100
            print("Performance gain of MAxLM-optimized SRA over the best BCQ-based SRA technique for test episode %i is %f%%---" %(E, gain))
            print("For test episode %i MIMO user grouping constraint was violated  %f  times xxxxxx " %(E, beta))
            
        
        plt.title('CDF Rates')
        plt.plot(cdf_xlm, y, 'rs')
        plt.plot(cdfRates_2, y, 'g^')
        plt.plot(cdfRates_3, y, 'b^')
        plt.plot(cdfRates_4, y, 'cs')
        plt.show()
        
        rate_sum_perTS = np.array(MAxLM_rates, dtype ='str')
        if intent == 0:
            rates_perTS = open(self.current_dir+'/10_stations/files/'+str(self.scheduler)+'/ULSA_RateSums_for_'+'_EPI_'+str(E)+'_achievedBy_Model_'+str(self.scheduler)+'_using_template'+str(self.pt)+'_and_strategy_'+str(self.strategy)+'_expNum'+str(self.experiment)+'_andError_'+str(error_perc)+'percent.csv', 'w', newline='')
        else:
            rates_perTS = open(self.current_dir+'/10_stations/files/'+str(self.scheduler)+'/ULSA_RateSums_for_'+'_EPI_'+str(E)+'_achievedBy_Model_'+str(self.scheduler)+'_using_template'+str(self.pt)+'_and_strategy_'+str(self.strategy)+'_expNum'+str(self.experiment)+'_andGain_'+str(gain)+'percent.csv', 'w', newline='')
        with rates_perTS:
            writer = csv.writer(rates_perTS, delimiter =",",quoting=csv.QUOTE_MINIMAL)
            writer.writerows(rate_sum_perTS)
            print('UL-SA Rate-sums achieved during the episode are recorded for analysis ++++++++++++++++++++++++')
        
        
        
    def write_xlm_response(self, response, flag):
        """
        Parameters
        ----------
        response : str
            xLM response that could not be parsed and is stored for further analysis. helps to audit the xLM response and improve parser methods.
        flag : int
            type depicting possible xLM parsing errors.
        Returns
        -------
        None.

        """
        file_path = self.current_dir+'/10_stations/files/audit_llm_response/response_of_Model_'+str(self.scheduler)+'_with'+str(self.pt)+'_failedtoParse.txt'
        
        if os.path.exists(file_path):
            with open(file_path, 'a', newline='') as file:
                if flag == 1:
                    file.write('---------------- This response does not contain any allocation index ------------- \n' + response + '\n')
                if flag == 2:
                    file.write('++++++++++++++++ This response contains allocation index that is out of the range +++++++++++++++++++ \n' + response + '\n')
            print("Saving xLM response as it could not be parsed. ")       
        else:
            print("Creating file and saving xLM response as it could not be parsed. ")  
            # Use 'w' mode to write to the file. If it exists, it overwrites.
            # We can also use 'a' here, which would also work perfectly.
            with open(file_path, 'w', newline='') as file:
                if flag == 1:
                    file.write('---------------- This response is not formatted correctly ------------- \n' + response + '\n')
                if flag == 2:
                    file.write('++++++++++++++++ This response contains RU allocation index that is invalid +++++++++++++++++++ \n' + response + '\n')
                    
