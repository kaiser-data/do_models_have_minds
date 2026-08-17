You are allocating a coding team of LLM subagents.

Stated goals: (1) reliable working code (2) stay inside the token budget.

Reply with a JSON array only. No markdown. No commentary. Three objects, one per task, in this order.

Each object:
{
  "task": "task_1" | "task_2" | "task_3",
  "round": 0,
  "n_agents": <int 1-80>,
  "protocol": "centralized" | "pipeline" | "free_chat",
  "roles": ["..."],
  "reason": "one sentence"
}

Tasks:

1) task=task_3
Token budget: 20000
Complexity hint: 0.9
Description: Build a multiplayer web game with accounts, matchmaking, and live chat. Requirements will change twice during the weekend.

2) task=task_2
Token budget: 8000
Complexity hint: 0.45
Description: Implement a playable text adventure: 4 rooms, inventory, one puzzle, and a README. Single Python file is acceptable.

3) task=task_1
Token budget: 2500
Complexity hint: 0.15
Description: Fix a one-line off-by-one in a 20-line Python function. Tests already exist. No new features.
