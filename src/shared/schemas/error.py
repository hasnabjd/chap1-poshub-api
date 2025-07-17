from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: bool = Field(True, description="Always true for error responses")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    status_code: int = Field(..., description="HTTP status code")
    error_type: str = Field(..., description="Type of error")
    details: list[ErrorDetail] = Field(..., description="List of error details")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": True,
                "timestamp": "2024-03-20T10:00:00Z",
                "status_code": 502,
                "error_type": "EXTERNAL_SERVICE_ERROR",
                "details": [
                    {
                        "code": "TIMEOUT",
                        "message": "Request timed out after 10 seconds",
                        "field": None
                    }
                ],
                "request_id": "req_123456"
            }
        }
    } 