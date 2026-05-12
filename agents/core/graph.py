from uuid import UUID, uuid4

from langgraph.graph import END, StateGraph

from agents.coding_agent import CodingAgent
from agents.core.memory import workspace_memory
from agents.core.state import WorkflowState, create_initial_state
from agents.planning_agent import PlanningAgent
from agents.presentation_agent import PresentationAgent
from agents.report_agent import ReportAgent
from agents.research_agent import ResearchAgent


class OmniAgentGraph:
    def __init__(
        self,
        planning_agent: PlanningAgent | None = None,
        research_agent: ResearchAgent | None = None,
        coding_agent: CodingAgent | None = None,
        report_agent: ReportAgent | None = None,
        presentation_agent: PresentationAgent | None = None,
    ) -> None:
        self.planning_agent = planning_agent or PlanningAgent()
        self.research_agent = research_agent or ResearchAgent()
        self.coding_agent = coding_agent or CodingAgent()
        self.report_agent = report_agent or ReportAgent()
        self.presentation_agent = presentation_agent or PresentationAgent()
        self.graph = self._compile()

    def _compile(self):
        graph = StateGraph(WorkflowState)
        graph.add_node("planning", self.planning_agent)
        graph.add_node("research", self.research_agent)
        graph.add_node("coding", self.coding_agent)
        graph.add_node("report", self.report_agent)
        graph.add_node("presentation", self.presentation_agent)

        graph.set_entry_point("planning")
        graph.add_edge("planning", "research")
        graph.add_edge("research", "coding")
        graph.add_edge("coding", "report")
        graph.add_edge("report", "presentation")
        graph.add_edge("presentation", END)
        return graph.compile()

    async def run(
        self,
        user_id: UUID,
        objective: str,
        conversation_id: UUID | None = None,
        workflow_id: UUID | None = None,
        document_ids: list[UUID] | None = None,
    ) -> WorkflowState:
        state = create_initial_state(
            workflow_id=workflow_id or uuid4(),
            user_id=user_id,
            conversation_id=conversation_id,
            objective=objective,
            document_ids=document_ids,
        )
        state = workspace_memory.hydrate(state)
        return await self.graph.ainvoke(state)


omniagent_graph = OmniAgentGraph()

