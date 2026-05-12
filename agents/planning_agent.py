import uuid
from typing import List
from agents.core.agent_base import BaseAgent
from agents.core.state import WorkflowState, AgentTask, AgentFinding
from agents.core.memory import shared_memory

PLANNING_PROMPT = """
You are the Lead OmniAgent Architect. Your job is to analyze the user's objective and break it down into a sequence of tasks for specialized agents.
Objective: {objective}

Available Agents:
- Research Agent: Deep context retrieval and information gathering.
- Coding Agent: Implementation design, code analysis, and prototyping.
- Report Agent: Technical synthesis and structured documentation.
- Presentation Agent: Executive summary and visual storytelling.

Create a plan that maximizes efficiency and quality.
"""

class PlanningAgent(BaseAgent):
    name = "planning"

    async def run(self, state: WorkflowState) -> WorkflowState:
        objective = state["objective"]
        
        # 1. 'Think' phase (LLM call simulation)
        analysis = await self.think(PLANNING_PROMPT.format(objective=objective), state)
        
        # 2. Decompose into tasks
        tasks = [
            AgentTask(
                id=str(uuid.uuid4()),
                agent="research",
                title="Context Gathering",
                objective=f"Retrieve all necessary background for: {objective}"
            ),
            AgentTask(
                id=str(uuid.uuid4()),
                agent="coding",
                title="Technical Design",
                objective=f"Design the system architecture for: {objective}",
                depends_on=["research"]
            ),
            AgentTask(
                id=str(uuid.uuid4()),
                agent="report",
                title="Technical Synthesis",
                objective=f"Write a detailed technical report for: {objective}",
                depends_on=["coding"]
            ),
            AgentTask(
                id=str(uuid.uuid4()),
                agent="presentation",
                title="Executive Summary",
                objective=f"Create a high-level presentation for: {objective}",
                depends_on=["report"]
            )
        ]
        
        # 3. Update state
        state["tasks"] = [task.model_dump() for task in tasks]
        state["status"] = "running"
        state["next_step"] = "research"
        
        # 4. Record finding
        finding = AgentFinding(
            agent=self.name,
            title="Strategic Roadmap Created",
            content=f"Decomposed objective into {len(tasks)} sequential tasks: Research -> Coding -> Report -> Presentation.",
            confidence=1.0
        )
        self.update_state(state, [finding])
        
        shared_memory.add_message(self.name, "Plan finalized and tasks dispatched.")
        
        return state
