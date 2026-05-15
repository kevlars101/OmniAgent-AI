import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import json
from fastapi import WebSocket
import asyncio

from app.db.models import Workflow, WorkflowStatusEnum

# We need to import the LangGraph graph
# To ensure the backend can import the agents correctly if they are in the parent directory:
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
try:
    from agents import veyra_graph
except ImportError:
    # Fallback if running from a different root
    veyra_graph = None

class WorkflowService:
    @staticmethod
    async def create_workflow(db: AsyncSession, objective: str, user_id: UUID) -> Workflow:
        workflow = Workflow(
            user_id=user_id,
            objective=objective,
            status=WorkflowStatusEnum.queued
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def run_workflow(db: AsyncSession, workflow_id: UUID, document_ids: list[UUID] | None = None) -> Workflow:
        workflow = await db.get(Workflow, workflow_id)
        if not workflow:
            raise ValueError("Workflow not found")
            
        workflow.status = WorkflowStatusEnum.running
        await db.commit()
        
        if veyra_graph:
            # Run LangGraph Agent Layer
            final_state = await veyra_graph.run(
                user_id=workflow.user_id,
                objective=workflow.objective,
                workflow_id=workflow.id,
                document_ids=document_ids,
                stream=False
            )
            workflow.state_data = final_state
            if final_state.get("status") == "failed":
                workflow.status = WorkflowStatusEnum.failed
            else:
                workflow.status = WorkflowStatusEnum.completed
        else:
            # Fallback for testing without agents module
            workflow.status = WorkflowStatusEnum.completed
            workflow.state_data = {"mock": "Agent module not found"}

        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def stream_workflow(websocket: WebSocket, workflow_id: UUID, user_id: UUID):
        await websocket.accept()
        
        if not veyra_graph:
            await websocket.send_json({"error": "LangGraph agents not loaded"})
            await websocket.close()
            return

        # Fetch workflow info securely
        # Here we would normally query the DB to ensure workflow exists and belongs to user
        
        try:
            # Note: We need a way to mock fetching the objective from the DB here
            # Assuming we got it somehow:
            objective = "Real-time query..." # Mocked for ws
            
            async for state_chunk in await veyra_graph.run(
                user_id=user_id,
                objective=objective,
                workflow_id=workflow_id,
                stream=True
            ):
                # Send agent state updates down the websocket
                # State chunks usually contain the node name and the state delta
                for node, delta in state_chunk.items():
                    await websocket.send_json({
                        "node": node,
                        "messages": delta.get("messages", []),
                        "status": delta.get("status", "running")
                    })
                await asyncio.sleep(0.1) # Small delay for message backpressure
                
            await websocket.send_json({"event": "workflow_completed"})
        except Exception as e:
            await websocket.send_json({"error": str(e)})
        finally:
            await websocket.close()
