ReAct : is a design pattern used in AI agentd that stands for Reasoning + Acting. It allows a language model (llm) to interleave internal reasoning(thought) with external actions (like tool use) in a structured, multi-step process.
Instead of generating an answer in one go, model thinks step by step, deciding what it needs to do next and optionally calling tools(API, calculators, web search etc) to help it.

ReAct : 1. thought 2. Action 3. observation

                         Agent ---------------> Agent Executor

to run agent we need agent executor (to run thought, action, observation step of agent)

AgentExecutor (AE) orchestrates the entire loop:

1. AE Sends inputs and previous messages to the agents
2. AE Gets the next action from agent
3. AE executes that tool with provided input
4. AE Adds the tools observation back into the history
5. AE Loops again updated history until the agent says final answer
