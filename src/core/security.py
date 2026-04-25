import re
import logging
import time
from typing import Optional, Dict
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

# Simple in-memory rate limiting for demonstration
# In production, use Redis or a similar store
rate_limit_store: Dict[str, float] = {}

def sanitize_input(text: str) -> str:
    """
    Robust sanitization of user input.
    
    Args:
        text: The raw user input.
        
    Returns:
        Sanitized text.
    """
    # Remove HTML tags more aggressively
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove potential script injections
    text = re.sub(r'javascript:', '', text)
    
    # Trim and normalize whitespace
    text = " ".join(text.split())
    
    # Basic length limit to prevent DoS via large strings
    return text[:1000]

async def verify_recaptcha(token: str) -> bool:
    """
    Placeholder for reCAPTCHA Enterprise verification.
    """
    if not token:
        logger.warning("Security Check: reCAPTCHA token missing.")
        return False
        
    logger.info("Security Check: reCAPTCHA token received.")
    return True

def apply_rate_limit(request: Request, limit_seconds: int = 2):
    """
    Applies a simple per-IP rate limit.
    """
    client_ip = request.client.host
    now = time.time()
    
    if client_ip in rate_limit_store:
        elapsed = now - rate_limit_store[client_ip]
        if elapsed < limit_seconds:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests. Please wait.")
            
    rate_limit_store[client_ip] = now
