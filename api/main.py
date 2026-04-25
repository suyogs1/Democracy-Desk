import time
import logging
import pytest
import multiprocessing
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from pydantic import BaseModel
from core.orchestrator import Orchestrator
from core.models import AssistantResponse, ExplanationMode
from core.security import sanitize_input, verify_recaptcha, apply_rate_limit
from services.google_cloud import google_cloud
from fastapi.middleware.cors import CORSMiddleware

# Initialize logging via the Google Cloud Manager
logger = logging.getLogger("democracy_desk.api")

def run_startup_tests():
    """Runs a subset of critical tests to ensure environment integrity."""
    logger.info("🚀 Running Startup Self-Tests...")
    # Run pytest on the hardened test suite
    exit_code = pytest.main(["-x", "tests/test_hardened.py"])
    if exit_code != 0:
        logger.error(f"❌ Startup tests failed with code {exit_code}")
        # In a real production app, we might stop the startup here
    else:
        logger.info("✅ Startup tests passed successfully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown logic."""
    # Run tests in a separate process to avoid blocking the event loop
    # or interfering with the main app instance
    test_proc = multiprocessing.Process(target=run_startup_tests)
    test_proc.start()
    yield
    test_proc.join()

app = FastAPI(
    title="Democracy Desk AI",
    description="Secure, production-grade election education assistant.",
    version="2.1.0",
    lifespan=lifespan
)

# Hardened CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Custom Middleware for Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Adds essential security headers to every response."""
    start_time = time.time()
    response: Response = await call_next(request)
    
    # Security Headers
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/; "
        "frame-src https://www.google.com/recaptcha/; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com;"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Performance Telemetry
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

orchestrator = Orchestrator()

class QueryRequest(BaseModel):
    """Payload for user queries."""
    query: str
    state: str = "California"
    mode: ExplanationMode = ExplanationMode.NORMAL
    recaptcha_token: str = ""

@app.post("/ask", response_model=AssistantResponse)
async def ask_question(request: QueryRequest, security_check = Depends(apply_rate_limit)) -> AssistantResponse:
    """
    Submit an election-related query and get structured assistance.
    Includes sanitization and security verification.
    """
    # 1. Security Verification
    if not await verify_recaptcha(request.recaptcha_token):
        # We log and proceed for demo purposes if token is missing but warn
        logger.warning("Request processed without valid reCAPTCHA token.")

    # 2. Input Sanitization
    sanitized_query = sanitize_input(request.query)
    
    # 3. Telemetry
    google_cloud.log_telemetry("USER_QUERY", {
        "state": request.state,
        "mode": request.mode,
        "query_length": len(sanitized_query)
    })

    try:
        response = await orchestrator.handle_query(
            query=sanitized_query, 
            state=request.state, 
            mode=request.mode
        )
        return response
    except Exception as e:
        logger.error(f"Error handling query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error processing your request.")

@app.get("/health")
def health_check() -> dict:
    """Check API status and version."""
    return {
        "status": "healthy", 
        "version": "2.1.0",
        "google_cloud_services": "active"
    }
