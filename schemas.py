from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class MCPError(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    ok: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[MCPError] = None
    request_id: str

    model_config = ConfigDict(extra="forbid")


# ---------- Tool #1: list events ----------
class ListEventsInput(BaseModel):
    range_start_ts: int = Field(ge=0)
    range_end_ts: int = Field(ge=0)
    calendar_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class CalendarEvent(BaseModel):
    event_id: str
    summary: str
    start_ts: int
    end_ts: int
    is_all_day: bool
    location: Optional[str] = None
    organizer: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


# ---------- Tool #2: create focus blocks ----------
class FocusBlock(BaseModel):
    start_ts: int = Field(ge=0)
    duration_min: int = Field(ge=15, le=480)

    model_config = ConfigDict(extra="forbid")


class CreateFocusBlocksInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    blocks: List[FocusBlock] = Field(min_length=1, max_length=10)
    description: Optional[str] = Field(default=None, max_length=2000)
    calendar_id: Optional[str] = None
    visibility: Optional[Literal["private", "public"]] = None
    free_busy_status: Optional[Literal["busy", "free"]] = None

    model_config = ConfigDict(extra="forbid")


# ---------- Tool #3: health check ----------
class HealthCheckInput(BaseModel):
    calendar_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")
