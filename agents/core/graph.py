from typing import Any, AsyncGenerator, Literal, List
from uuid import UUID, uuid4
import logging

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from agents.core.state import WorkflowState, create_initial_state
from agents.core.memory import shared_memory
from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from agents.coding_agent import CodingAgent
from agents.report_agent import ReportAgent
from agents.presentation_agent import PresentationAgent

logger = logging.getLogger(__name__)

def router(state: WorkflowState) -> Literal["research", "coding", "report", "presentation", "__end__"]:
    """
    Conditional router that determines the next agent to execute.
    """
    next_step = state.get("next_step")
    
    if state["status"] == "failed":
        logger.error(f"Workflow failed: {state.get('errors')}")
        return "__end__"
    
    if next_step == "research":
        return "research"
    elif next_step == "coding":
        return "coding"
    elif next_step == "report":
        return "report"
    elif next_step == "presentation":
        return "presentation"
    
    return "__end__"

class OmniAgentGraph:
    def __init__(self):
        self.builder = StateGraph(WorkflowState)
        self._register_nodes()
        self._register_edges()
        self.graph = self.builder.compile()

    def _register_nodes(self):
        self.builder.add_node("planning", PlanningAgent())
        self.builder.add_node("research", ResearchAgent())
        self.builder.add_node("coding", CodingAgent())
        self.builder.add_node("report", ReportAgent())
        self.builder.add_node("presentation", PresentationAgent())

    def _register_edges(self):
        # Entry point
        self.builder.set_entry_point("planning")
        
        # Planning always goes to Router
        self.builder.add_conditional_edges(
            "planning",
            router,
            {
                "research": "research",
                "coding": "coding",
                "report": "report",
                "presentation": "presentation",
                "__end__": END
            }
        )
        
        # Each agent goes back to Router for the next step
        self.builder.add_conditional_edges("research", router, {
            "coding": "coding",
            "__end__": END
        })
        self.builder.add_conditional_edges("coding", router, {
            "report": "report",
            "__end__": END
        })
        self.builder.add_conditional_edges("report", router, {
            "presentation": "presentation",
            "__end__": END
        })
        self.builder.add_conditional_edges("presentation", router, {
            "__end__": END
        })

    async def run(
        self,
        user_id: UUID,
        objective: str,
        conversation_id: UUID | None = None,
        workflow_id: UUID | None = None,
        document_ids: List[UUID] | None = None,
        stream: bool = False
    ) -> WorkflowState | AsyncGenerator[dict, Any]:
        """
        Executes the workflow with optional streaming.
        """
        initial_state = create_initial_state(
            workflow_id=workflow_id or uuid4(),
            user_id=user_id,
            objective=objective,
            conversation_id=conversation_id,
            document_ids=document_ids
        )
        
        if stream:
            return self.graph.astream(initial_state)
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state

# Main instance
omniagent_graph = OmniAgentGraph()
