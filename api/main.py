"""
FastAPI Entry Point for Democracy Desk.
Provides endpoints for AI assistance and system health.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.orchestrator import Orchestrator
from core.models import AssistantResponse, ExplanationMode
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Democracy Desk API",
    description="Multi-agent AI for election education regional guidance.",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class QueryRequest(BaseModel):
    """Payload for user queries."""
    query: str
    state: str = "California"
    mode: ExplanationMode = ExplanationMode.NORMAL

@app.post("/ask", response_model=AssistantResponse)
async def ask_question(request: QueryRequest) -> AssistantResponse:
    """
    Submit an election-related query and get structured assistance.
    """
    try:
        response = await orchestrator.handle_query(
            query=request.query, 
            state=request.state, 
            mode=request.mode
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check() -> dict:
    """Check API status."""
    return {"status": "healthy", "version": "2.0.0"}
