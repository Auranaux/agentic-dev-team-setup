from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
from app.orchestrator.slots import SlotManager, ConversationSlots
from app.orchestrator.generator import PRDGenerator
from app.orchestrator.llm.factory import get_llm_client

router = APIRouter()

conversations: Dict[str, ConversationSlots] = {}

class StartIntakeRequest(BaseModel):
    project_name: Optional[str] = None

class StartIntakeResponse(BaseModel):
    conversation_id: str
    message: str

class AnswerRequest(BaseModel):
    conversation_id: str
    slot_name: str
    value: Any

class AnswerResponse(BaseModel):
    slots: Dict[str, Any]
    gaps: List[str]
    next_question: Optional[str]

class StatusResponse(BaseModel):
    slots: Dict[str, Any]
    gaps: List[str]
    next_question: Optional[str]

class CommitRequest(BaseModel):
    conversation_id: str

class CommitResponse(BaseModel):
    artifacts: List[str]
    message: str

@router.post("/start", response_model=StartIntakeResponse)
async def start_intake(request: StartIntakeRequest):
    """Start a new intake conversation"""
    conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
    slot_manager = SlotManager()
    conversations[conversation_id] = slot_manager.create_conversation()
    
    return StartIntakeResponse(
        conversation_id=conversation_id,
        message="Intake started. Please provide project details."
    )

@router.post("/answer", response_model=AnswerResponse)
async def answer_question(request: AnswerRequest):
    """Answer a slot filling question"""
    if request.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[request.conversation_id]
    slot_manager = SlotManager()
    
    setattr(conversation, request.slot_name, request.value)
    
    gaps = slot_manager.get_gaps(conversation)
    next_question = slot_manager.get_next_question(gaps) if gaps else None
    
    return AnswerResponse(
        slots=conversation.dict(),
        gaps=gaps,
        next_question=next_question
    )

@router.get("/status", response_model=StatusResponse)
async def get_status(conversation_id: str):
    """Get current conversation status"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[conversation_id]
    slot_manager = SlotManager()
    gaps = slot_manager.get_gaps(conversation)
    next_question = slot_manager.get_next_question(gaps) if gaps else None
    
    return StatusResponse(
        slots=conversation.dict(),
        gaps=gaps,
        next_question=next_question
    )

@router.post("/commit", response_model=CommitResponse)
async def commit_intake(request: CommitRequest):
    """Generate PRD and update API contracts"""
    if request.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[request.conversation_id]
    slot_manager = SlotManager()
    
    gaps = slot_manager.get_gaps(conversation)
    if gaps:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required information: {', '.join(gaps)}"
        )
    
    generator = PRDGenerator()
    artifacts = await generator.generate_artifacts(conversation)
    
    return CommitResponse(
        artifacts=artifacts,
        message="PRD generated and contracts updated successfully"
    )
