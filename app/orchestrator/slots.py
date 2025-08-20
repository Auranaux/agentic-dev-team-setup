from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ConversationSlots(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    target_users: Optional[str] = None
    key_features: Optional[List[str]] = None
    technical_requirements: Optional[str] = None
    success_metrics: Optional[str] = None
    timeline: Optional[str] = None
    budget_constraints: Optional[str] = None
    integration_requirements: Optional[List[str]] = None
    data_entities: Optional[List[str]] = None

class SlotManager:
    """Manages slot filling logic and validation"""
    
    REQUIRED_SLOTS = [
        "project_name",
        "project_description", 
        "target_users",
        "key_features"
    ]
    
    SLOT_QUESTIONS = {
        "project_name": "What is the name of your project?",
        "project_description": "Please provide a brief description of your project.",
        "target_users": "Who are the target users for this project?",
        "key_features": "What are the key features you want to implement? (comma-separated list)",
        "technical_requirements": "Do you have any specific technical requirements?",
        "success_metrics": "How will you measure the success of this project?",
        "timeline": "What is your target timeline for this project?",
        "budget_constraints": "Are there any budget constraints we should consider?",
        "integration_requirements": "Do you need to integrate with any external systems?",
        "data_entities": "What are the main data entities in your system? (e.g., users, products, orders)"
    }
    
    def create_conversation(self) -> ConversationSlots:
        """Create a new conversation with empty slots"""
        return ConversationSlots()
    
    def get_gaps(self, conversation: ConversationSlots) -> List[str]:
        """Get list of unfilled required slots"""
        gaps = []
        for slot in self.REQUIRED_SLOTS:
            value = getattr(conversation, slot)
            if value is None or (isinstance(value, list) and len(value) == 0):
                gaps.append(slot)
        return gaps
    
    def get_next_question(self, gaps: List[str]) -> Optional[str]:
        """Get the next question to ask based on gaps"""
        if not gaps:
            return None
        return self.SLOT_QUESTIONS.get(gaps[0])
    
    def validate_slot_value(self, slot_name: str, value: Any) -> bool:
        """Validate a slot value"""
        if slot_name in ["key_features", "integration_requirements", "data_entities"]:
            if isinstance(value, str):
                return len(value.strip()) > 0
            elif isinstance(value, list):
                return len(value) > 0
        return value is not None and str(value).strip() != ""
