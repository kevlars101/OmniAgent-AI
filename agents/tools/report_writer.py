from typing import Any
from agents.core.state import AgentFinding


class ReportWriterTool:
    name = "report_writer"

    def compose_markdown(self, objective: str, findings: list[AgentFinding]) -> str:
        sections = [f"# Report\n\nObjective: {objective}\n"]
        for finding in findings:
            citations = ""
            if finding.citations:
                citations = "\n\nCitations:\n" + "\n".join(f"- {citation}" for citation in finding.citations)
            sections.append(f"## {finding.title}\n\n{finding.content}{citations}\n")
        return "\n".join(sections).strip()

    async def ainvoke(self, kwargs: dict) -> Any:
        return self.compose_markdown(**kwargs)

