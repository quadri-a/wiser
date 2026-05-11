import numpy as np

class scheduling_engine:
    def __init__(self, n_sta, n_ru, n_ap):
        
        self.n_sta = n_sta
        self.n_ru = n_ru
        self.n_ap = n_ap
        
    def random_actions(self):
        """
        Returns
        -------
        actions : int
            NxR matrix containing randomly assignment of the N agents over R resources.
        """
        actions = np.array(np.zeros((self.n_sta, self.n_ru)), dtype='int')
        for i in range(self.n_sta):
            actions[i,:] = np.random.randint(0, 2, size=self.n_ru)
        
        return actions
    
    async def send_request(self, client, model, prompt):
        try:
            response = await client.chat(model=model, messages=[{'role': 'user', 'content': prompt}]) #, options={'num_ctx': 32000 }
            return response['message']['content']
        
        except Exception:
            print("Error processing")
            return None    
    
    async def xlm_scheduler(self, client, model_name, prompt):
        """
        Parameters
        ----------
        client : instance of asynchronous connections.
        model_name : str
            xLM model name
        prompt : str
            N prompts for SRA.

        Returns
        -------
        batch_response : dict
            contains xLM's SRA intent in terms of RU assignments and reasoning.

        """
        batch_response = await self.send_request(client, model_name, prompt)
        return batch_response

    
    def BCQ_scheduler(self, CSI):
        """
        The following code implementing best channel quality-based scheduler is generated using Llama3.1:8b 
        Parameters
        ----------
        CSI : float
            NxR matrix containing AP-STA channel conditions.

        Returns
        -------
        S : int
            binary RU assignment matrix assigning the nine resources to M STAs with highest channel gains.
        """
        # Define parameters
        N = CSI.shape[0]  # Number of users
        R = CSI.shape[1]  # Number of channels
        M = self.n_ap  # Number of antennas (assuming square root)

        # Initialize scheduling matrix S
        S = np.zeros((N, R))
        # Iterate over each channel
        for r in range(R):
            # Get the indices of the {M} users with the highest CSI over this channel
            idx = np.argsort(CSI[:, r], axis=0)[-M:]
            # Assign 1 to these users in the scheduling matrix S
            S[idx, r] = 1

        return S









