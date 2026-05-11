"""
Modular prompts defining the xLM's role, task, and characterizing each agent's environment.
xLM response format: The instructions informing the xLM on how to format its repsonse is also included within the prompt.
parsing errors: system notifications to characterize different types of xLM parsing errors are also included here.
"""


role_task_MAxLM = """ You are a WiSER assistant performing resource allocation for Agent{i}.
- Agent{i} resides with {n_sta-1} other agents in a well-observed environment where the state of the environment changes over time.
- These agents can share the {n_ru} resources: RU1, RU2, RU3, RU4, RU5, RU6, RU7, RU8, and RU9 among each other to execute desired actions to accomplish their tasks.
- Your task is to allocate the resources to Agent{i}, based on the following resource allocation strategy.
Resource Allocation Strategy: {strategy}    
Agent{i}'s current state St{ts} in the environment provides information on how strong and compatible the agent is compared to other agents over the {n_ru} resources.
"""

role_task_BCQ = """ You are a WiSER assistant performing resource allocation for Agent{i}.
- Agent{i} resides with {n_sta-1} other agents in a well-observed environment where the state of the environment changes over time.
- These agents can share the {n_ru} resources: RU1, RU2, RU3, RU4, RU5, RU6, RU7, RU8, and RU9 among each other to execute desired actions to accomplish their tasks.
- Your task is to allocate the resources to Agent{i}, based on the following resource allocation strategy.
Resource Allocation Strategy: {strategy}    
Agent{i}'s current state in the environment provides information on how strong the agent is over the {n_ru} resources.
"""

parsing_instructions = """In your response, state the resource allocation array and the reasoning behind your resource allocation strategy. Please, do not suggest codes, other methods or example cases to generate the Resource Allocation array.\n """

parser_error = """Note, in the previous state Agent{i} could not retrieve the "resource_allocation_array" within your response. Therefore, Agent{i} couldn't be allocated any of the available resources, which adversely impacted Agent{i}'s performance and disrupted agent's operation. \n"""

parser_error_out_of_Range = """Note, in the previous state Agent{i} could not be allocated any of the available resources. This is because the resource allocation array has more then {n_ru} indexes, or includes integers other then 1 to 9. 
Therefore, Agent{i} couldn't be allocated any of the {n_ru} resources, which adversely impacted Agent{i}'s performance as the agent was deprived of the resources to operate.\n """


strategy_response_format = """To enforce your resource allocation strategy, express your resource allocation intent using the resource_allocation_array, where resource or RU numbers represent the assignment of the resources. For example:
    - To allocate all of the {n_ru} resources to Agent{i}, update the resource_allocation_array with the resource or RU numbers of the {n_ru} resources (i.e., "resource_allocation_array": [1, 2, 3, 4, 5, 6, 7, 8, 9]).
    - To allocate none of the {n_ru} resources to Agent{i}, return an empty resource_allocation_array (i.e., "resource_allocation_array": []).
    - To allocate some of the {n_ru} resources to Agent{i}, such as RU4 and RU9, update the resource_allocation_array with the resource or RU numbers of the selected resources (i.e., "resource_allocation_array": [4, 9]).
   
Note, Agent{i} solely depends on you for resource allocation and will scan your response to retrieve the "resource_allocation_array". \n
"""

json_format_example_allocation = """The output should be formatted as a JSON instance that conforms to the JSON schema below.
Here is the output schema:
```
{{"resource_allocation_array": [?,?,?], "reasoning": "This field is a string type that contains any step-wise analysis of agent's state and the reasoning behind the selection of the resources."}}
```
Strictly follow the above format. In JSON schema there is a key and a value for the key. For example, {{"key": value}}. Do NOT include any comments or explanation after the value. 
For example, do not format your JSON output as {{"resource_allocation_array": [?,?,?,?,?,?,?,?,?] // This is an example allocation, "reasoning": "analysis of resource allocation strategy for Agent"}} as the agent will fail to retrieve the resource allocations due to the comments after the resource_allocation_array."""

json_schema_for_SRA = """The output should be formatted as a JSON instance that conforms to the JSON schema below.
Here is the output schema:
```
{{"resource_allocation_array": [?,?,?], "reasoning": "This field is a string type that contains any step-wise analysis of agent's state and the reasoning behind the selection of the resources."}}
```
Strictly follow the above format. In JSON schema there is a key and a value for the key. For example, {{"key": value}}. Do NOT include any comments or explanation after the value. 
For example, do not format your JSON output as {{"resource_allocation_array": [?,?,?,?,?,?,?,?,?] // This is an example allocation, "reasoning": "analysis of resource allocation strategy for Agent"}} as the agent will fail to retrieve the resource allocations due to the comments after the resource_allocation_array."""


