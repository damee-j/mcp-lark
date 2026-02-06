from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MCPException(Exception):
    code: str
    message: str
    http_status: int = 500
    details: Optional[Dict[str, Any]] = None

    def to_error(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details or {},
        }


# --- Standard error factories ---
def invalid_argument(message: str, details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("MCP_INVALID_ARGUMENT", message, http_status=400, details=details)

def internal_error(message: str, details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("MCP_INTERNAL", message, http_status=500, details=details)

def auth_required(message: str = "Lark authentication required.", details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("LARK_AUTH_REQUIRED", message, http_status=401, details=details)

def permission_denied(message: str = "Permission denied.", details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("LARK_PERMISSION_DENIED", message, http_status=403, details=details)

def rate_limited(message: str = "Rate limited.", details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("LARK_RATE_LIMITED", message, http_status=429, details=details)

def upstream_error(message: str = "Upstream error.", details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("LARK_UPSTREAM_ERROR", message, http_status=502, details=details)

def create_conflict(message: str = "Event create conflict.", details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("CAL_EVENT_CREATE_CONFLICT", message, http_status=409, details=details)

def time_range_invalid(message: str = "Invalid time range.", details: Optional[Dict[str, Any]] = None) -> MCPException:
    return MCPException("CAL_TIME_RANGE_INVALID", message, http_status=400, details=details)
