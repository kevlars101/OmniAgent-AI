from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

from agents.core.state import AgentName, WorkflowState, AgentFinding
from agents.core.memory import shared_memory

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    name: AgentName

    def __init__(self, model: Any = None, tools: List[Any] | None = None):
        self.model = model
        self.tools = tools or []

    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """
        The entry point for LangGraph nodes.
        """
        logger.info(f"Agent {self.name} invoked")
        try:
            # 1. Update active agent and iteration count
            state["active_agent"] = self.name
            state["iteration_count"] += 1
            
            # 2. Run the agent logic
            updated_state = await self.run(state)
            
            # 3. Finalize state
            return updated_state
        except Exception as e:
            logger.error(f"Error in agent {self.name}: {str(e)}")
            state["errors"].append(f"[{self.name}] {str(e)}")
            state["status"] = "failed"
            return state

    @abstractmethod
    async def run(self, state: WorkflowState) -> WorkflowState:
        """Main execution logic for the agent."""
        pass

    async def think(self, prompt: str, state: WorkflowState) -> str:
        """
        Simulate a thinking process (LLM call).
        In a real implementation, this would call Gemini or OpenAI.
        """
        logger.info(f"{self.name} is thinking...")
        # This is where the LLM interaction would happen
        # placeholder for actual LLM call
        return f"Processed prompt with context: {state['objective']}"

    async def use_tools(self, tool_name: str, **kwargs) -> Any:
        """Execute a specific tool."""
        logger.info(f"{self.name} using tool: {tool_name}")
        # Dynamic tool execution logic
        for tool in self.tools:
            if hasattr(tool, "name") and tool.name == tool_name:
                return await tool.ainvoke(kwargs)
        return f"Tool {tool_name} not found."

    def update_state(self, state: WorkflowState, findings: List[AgentFinding]) -> WorkflowState:
        """Update state with new findings."""
        for finding in findings:
            state["findings"].append(finding.model_dump())
            shared_memory.add_finding(finding)
        return state
