# src/api/endpoints.py

from fastapi import FastAPI, HTTPException, Depends, Request, status, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, validator
from typing import List, Optional
from uuid import UUID, uuid4
import logging
import asyncio
import jwt
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import os
import re

# Import custom middleware
from src.api.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)

# Initialize FastAPI application
app = FastAPI(
    title="Real-Time Cyber Threat Detection and Response System",
    version="1.0.0",
    description="Enterprise-grade API for real-time cyber threat detection and response.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Get CORS origins from environment or use defaults
cors_origins_env = os.getenv("CORS_ORIGINS", "")
origins = cors_origins_env.split(",") if cors_origins_env else [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - last added is executed first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
    requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")

# JWT Secret and Expiry Configuration (from environment variables)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-CHANGE-IN-PRODUCTION")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Validate JWT_SECRET in production
if os.getenv("ENVIRONMENT") == "production" and JWT_SECRET == "dev-jwt-secret-CHANGE-IN-PRODUCTION":
    raise ValueError("JWT_SECRET must be set in production environment!")

# Models
class ThreatDetectionRequest(BaseModel):
    ip_address: str = Field(..., description="IPv4 address to analyze")
    user_agent: Optional[str] = Field(None, max_length=512, description="User agent string of the client")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the request")
    
    @validator("ip_address")
    def validate_ip_address(cls, v):
        """Validate IPv4 address format."""
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(ipv4_pattern, v):
            raise ValueError("Invalid IPv4 address format")
        # Validate each octet is 0-255
        octets = v.split(".")
        if not all(0 <= int(octet) <= 255 for octet in octets):
            raise ValueError("IPv4 address octets must be between 0 and 255")
        return v

class ThreatDetectionResponse(BaseModel):
    request_id: UUID
    threat_level: str
    details: Optional[str] = None

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[str] = None

# Custom Exception Classes
class ThreatDetectionException(Exception):
    def __init__(self, code: str, message: str, details: Optional[str] = None):
        self.code = code
        self.message = message
        self.details = details

@app.exception_handler(ThreatDetectionException)
async def threat_detection_exception_handler(request: Request, exc: ThreatDetectionException):
    logger.error(f"Error occurred: {exc.message} | Details: {exc.details} | Request ID: {request.headers.get('X-Request-ID')}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": exc.code, "message": exc.message, "details": exc.details},
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation error: {exc.errors()} | Request ID: {request.headers.get('X-Request-ID')}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"code": "validation_error", "message": "Invalid input", "details": exc.errors()},
    )

@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Authentication Dependency
def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Extract and validate JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value (format: "Bearer <token>")
    
    Returns:
        str: Username from token payload
        
    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use Bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Business Logic
async def analyze_threat(ip_address: str, user_agent: Optional[str]) -> dict:
    # Simulate async threat analysis (replace with actual ML model inference)
    await asyncio.sleep(1)  # Simulate processing time
    if ip_address.startswith("192.168"):
        return {"threat_level": "low", "details": "Private IP address detected"}
    elif ip_address.startswith("10."):
        return {"threat_level": "medium", "details": "Suspicious activity detected"}
    else:
        return {"threat_level": "high", "details": "Potential malicious activity detected"}

# Endpoints
@app.post("/api/v1/threat-detection", response_model=ThreatDetectionResponse, responses={400: {"model": ErrorResponse}})
async def detect_threat(
    detection_request: ThreatDetectionRequest,
    request: Request,
    user: str = Depends(get_current_user)
):
    """
    Endpoint to detect cyber threats based on IP address and user agent.
    
    Args:
        detection_request: Threat detection request payload
        request: FastAPI request object
        user: Authenticated username from JWT token
    
    Returns:
        ThreatDetectionResponse: Detection results with threat level and details
    
    Raises:
        ThreatDetectionException: If threat detection fails
    """
    try:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.info(
            f"Processing threat detection for IP: {detection_request.ip_address} | User: {user} | Request ID: {request_id}"
        )
        result = await analyze_threat(detection_request.ip_address, detection_request.user_agent)
        return ThreatDetectionResponse(
            request_id=uuid4(),  # Generate new UUID for response
            threat_level=result["threat_level"],
            details=result["details"],
        )
    except ValueError as e:
        logger.error(f"Validation error during threat detection: {str(e)}")
        raise ThreatDetectionException(code="validation_error", message="Invalid input data", details=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during threat detection: {str(e)}")
        raise ThreatDetectionException(code="internal_error", message="An unexpected error occurred", details=str(e))

@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service availability.
    """
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

@app.get("/api/v1/readiness", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint to verify service readiness.
    """
    return {"status": "ready", "timestamp": datetime.now(timezone.utc)}

# Additional Models for new endpoints
class ThreatStatistics(BaseModel):
    total_threats_detected: int
    threats_by_level: dict
    recent_threats: int
    timestamp: datetime

class ApiInfo(BaseModel):
    name: str
    version: str
    environment: str
    endpoints: int
    uptime: float

@app.get("/api/v1/info", response_model=ApiInfo, status_code=status.HTTP_200_OK)
async def api_info():
    """
    Get API information and metadata.
    """
    return ApiInfo(
        name="Real-Time Cyber Threat Detection and Response System",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development"),
        endpoints=len(app.routes),
        uptime=0.0  # Would be calculated from start time in production
    )

@app.get("/api/v1/statistics", response_model=ThreatStatistics, status_code=status.HTTP_200_OK)
async def get_statistics(user: str = Depends(get_current_user)):
    """
    Get threat detection statistics.
    
    Requires authentication.
    """
    # In production, this would query the database
    return ThreatStatistics(
        total_threats_detected=1234,
        threats_by_level={
            "low": 500,
            "medium": 400,
            "high": 300,
            "critical": 34
        },
        recent_threats=45,
        timestamp=datetime.now(timezone.utc)
    )

@app.post("/api/v1/auth/token")
async def generate_token(username: str, password: str):
    """
    Generate a JWT token for authentication.
    
    This is a simplified endpoint for demo purposes.
    In production, implement proper user authentication against database.
    """
    # In production: verify username and password against database
    # For demo: just generate a token
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    # Create token
    token_data = {
        "sub": username,
        "email": f"{username}@example.com"
    }
    expires = timedelta(minutes=JWT_EXPIRY_MINUTES)
    expire_time = datetime.now(timezone.utc) + expires
    token_data["exp"] = expire_time
    
    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRY_MINUTES * 60,
        "expires_at": expire_time.isoformat()
    }

# Graceful Shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application gracefully...")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)