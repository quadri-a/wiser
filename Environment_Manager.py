import numpy as np

class EnvironmentManager:
    def __init__(self, n_sta, n_ru, n_ap, ts):
        
        self.n_sta = n_sta
        self.n_ru = n_ru
        self.n_ap = n_ap
        self.ts = ts


    def access_point_terminal(self, state_observations, schedule, impact_factors, eng):
        """
        Parameters
        ----------
        state_observations : float
            contains information on AP-STA channel conditions (NxR), SNR (NxR), noise (1xR)
        schedule : dict
            contains the NxR resource assignment or user schedule and agent's observation for the current state of the WLAN environment.
        impact_factors : float
            NxR matrix with impact factors of all agent sover the nine resources (measure of spatial compatibility).
        eng : instance of the MATLAB engine object.

        Returns
        -------
        next_state_feed : dict
            contains information on UL rate-sum (NxR), revised RU assignments(NxR), original RU assignments (NxR), parsing errors(1xN), MIMO spatial constraint violations.

        """
        
        current_info = state_observations
        actions = np.array(schedule["actions"])
        
        flag_responseFails = np.array(schedule["flag_responseFails"])
        
        final_actions = np.array((np.zeros((self.n_sta,self.n_ru))), dtype='int')
        new_actions = np.matrix(np.ones((self.n_sta, self.n_ru)), dtype ='float32')
        # Process UL-SA feedback parameters
        SINR = np.array(np.zeros((self.n_sta, self.n_ru)), dtype = 'float32')
        rate = np.array(np.zeros((self.n_sta, self.n_ru)), dtype = 'float32')
        
        bad_rus = []
        violation = 0
        group_size = np.sum(actions,0)
        for ru in range(self.n_ru):
            if group_size[ru] > self.n_ap:
                violation = violation + 1
                bad_rus.append(ru)
        
        if violation > 0:
            bad_rus = np.array(bad_rus) # the append opearation above defines bad_ru as a list -> convert to array or perform list opeartions
            for users in range(violation):
                new_actions = np.multiply(new_actions, np.multiply(actions,(1-actions[:,bad_rus[users]]).reshape(self.n_sta,1)))
            final_actions = new_actions
        else:
            final_actions = actions 
            
        # Initiate TB UL-SA---using matlab engine-- by simulating WLAN UL-SA
    
        SINR, rate, nullsp_gain, ul_pow = eng.marl_ul_env_opt_2(current_info, final_actions, nargout=4) 
        
        rate_sum = np.sum(np.array(rate))
        
        next_state_feed  = {"ratesN": rate_sum, "final_actions": final_actions, "violations":violation, "current_actions": actions, "flag_responseFails":flag_responseFails}
        return next_state_feed
    