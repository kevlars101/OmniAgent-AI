from agents.core.agent_base import BaseAgent
from agents.core.memory import workspace_memory
from agents.core.state import AgentFinding, WorkflowState
from agents.tools.code_executor import CodeAnalysisTool


class CodingAgent(BaseAgent):
    name = "coding"

    def __init__(self, code_tool: CodeAnalysisTool | None = None) -> None:
        self.code_tool = code_tool or CodeAnalysisTool()

    async def run(self, state: WorkflowState) -> WorkflowState:
        research = next(
            (finding for finding in reversed(state["findings"]) if finding["agent"] == "research"),
            None,
        )
        research_summary = research["content"] if research else ""
        plan = self.code_tool.create_implementation_plan(state["objective"], research_summary)
        workspace_memory.set_artifact(state["workflow_id"], "implementation_plan", plan)
        workspace_memory.add_finding(
            state["workflow_id"],
            AgentFinding(
                agent=self.name,
                title="Implementation guidance",
                content="\n".join(f"- {step}" for step in plan["steps"]),
                confidence=0.82,
            ),
        )
        return state

