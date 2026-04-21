from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ExplanationMode(str, Enum):
    NORMAL = "normal"
    SIMPLE = "ELI10"

class Step(BaseModel):
    """Represents a single step in the election process."""
    title: str = Field(..., description="The title of the step")
    description: str = Field(..., description="Detailed explanation of the step")
    cta: str = Field(..., description="Call to action for the user")
    status: str = Field("pending", description="Status of the step: pending or completed")
    timeline_hint: Optional[str] = Field(None, description="When this step should be taken")

class IntentInfo(BaseModel):
    """Structured intent gathered from the user query."""
    intent: str
    category: str
    confidence: float

class TodayAction(BaseModel):
    """The recommended action for the user today."""
    action: str
    time_estimate: str
    urgency: UrgencyLevel

class ReasoningLog(BaseModel):
    """Structured reasoning for display in the UI."""
    agent_name: str
    summary: str = Field(..., max_length=200, description="Max 2 line summary of reasoning")
    confidence: float

class AssistantResponse(BaseModel):
    """Final response returned to the frontend."""
    query: str
    state: str
    intent: IntentInfo
    steps: List[Step]
    today_action: TodayAction
    final_explanation: str
    reasoning_log: List[ReasoningLog]
