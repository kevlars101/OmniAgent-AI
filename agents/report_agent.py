from agents.core.agent_base import BaseAgent
from agents.core.memory import workspace_memory
from agents.core.state import AgentFinding, WorkflowState
from agents.tools.report_writer import ReportWriterTool


class ReportAgent(BaseAgent):
    name = "report"

    def __init__(self, writer: ReportWriterTool | None = None) -> None:
        self.writer = writer or ReportWriterTool()

    async def run(self, state: WorkflowState) -> WorkflowState:
        findings = [AgentFinding.model_validate(item) for item in state["findings"]]
        markdown = self.writer.compose_markdown(state["objective"], findings)
        workspace_memory.set_artifact(state["workflow_id"], "report_markdown", markdown)
        workspace_memory.add_finding(
            state["workflow_id"],
            AgentFinding(
                agent=self.name,
                title="Report generated",
                content="Generated a markdown report artifact from the shared workspace findings.",
                confidence=0.9,
            ),
        )
        return state

