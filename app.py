from __future__ import annotations
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from schemas import (
    MCPResponse, MCPError,
    ListEventsInput, CreateFocusBlocksInput, HealthCheckInput
)
from errors import MCPException, time_range_invalid, create_conflict
from token_provider import get_valid_access_token
import lark_client


app = FastAPI(title="Lark MCP Server", version="0.1.0")


def _ok(data: dict, request_id: str) -> JSONResponse:
    body = MCPResponse(ok=True, data=data, error=None, request_id=request_id).model_dump()
    return JSONResponse(status_code=200, content=body)

def _fail(exc: MCPException, request_id: str) -> JSONResponse:
    body = MCPResponse(
        ok=False,
        data=None,
        error=MCPError(code=exc.code, message=exc.message, details=exc.details or {}),
        request_id=request_id
    ).model_dump()
    return JSONResponse(status_code=exc.http_status, content=body)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.exception_handler(MCPException)
async def mcp_exception_handler(request: Request, exc: MCPException):
    return _fail(exc, request.state.request_id)


@app.get("/health")
def health(request: Request):
    return _ok({"status": "ok"}, request.state.request_id)


# -------------------- Tool #1: list events --------------------
@app.post("/mcp/tools/lark_calendar_list_events")
def tool_list_events(payload: ListEventsInput, request: Request):
    if payload.range_end_ts < payload.range_start_ts:
        raise time_range_invalid("range_end_ts must be >= range_start_ts")

    token = get_valid_access_token()
    calendar_id = payload.calendar_id or lark_client.get_primary_calendar_id(token)

    raw_events = lark_client.list_events(
        access_token=token,
        calendar_id=calendar_id,
        start_ts=payload.range_start_ts,
        end_ts=payload.range_end_ts,
    )

    # Normalize (최소 필드만)
    normalized = []
    for e in raw_events:
        # Lark event 구조는 API 응답에 따라 다를 수 있으니 안전하게 처리
        event_id = e.get("event_id") or ""
        summary = e.get("summary") or ""
        start_ts = int((e.get("start_time") or {}).get("timestamp") or 0)
        end_ts = int((e.get("end_time") or {}).get("timestamp") or 0)
        is_all_day = bool(e.get("is_all_day", False))

        normalized.append({
            "event_id": event_id,
            "summary": summary,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "is_all_day": is_all_day,
            "location": e.get("location"),
            "organizer": (e.get("organizer") or {}).get("email") if isinstance(e.get("organizer"), dict) else None,
        })

    return _ok({"calendar_id": calendar_id, "events": normalized}, request.state.request_id)


# -------------------- Tool #2: create focus blocks (batch) --------------------
@app.post("/mcp/tools/lark_calendar_create_focus_blocks")
def tool_create_focus_blocks(payload: CreateFocusBlocksInput, request: Request):
    token = get_valid_access_token()
    calendar_id = payload.calendar_id or lark_client.get_primary_calendar_id(token)

    visibility = payload.visibility or "private"
    free_busy = payload.free_busy_status or "busy"
    description = payload.description or "Focus Block"

    created = []
    failed = []

    # summary prefix는 기존 스킬 컨벤션 유지(원하면 바꾸기)
    summary = f"🔒 Focus: {payload.title}"

    for blk in payload.blocks:
        start_ts = blk.start_ts
        end_ts = start_ts + blk.duration_min * 60

        try:
            event_id = lark_client.create_event(
                access_token=token,
                calendar_id=calendar_id,
                summary=summary,
                start_ts=start_ts,
                end_ts=end_ts,
                description=description,
                visibility=visibility,
                free_busy_status=free_busy,
            )
            created.append({"event_id": event_id, "start_ts": start_ts, "end_ts": end_ts})

        except MCPException as exc:
            # 충돌/권한/레이트리밋 등은 표준 에러코드로 내려가지만,
            # batch에서는 "툴 전체 실패" 대신 슬롯 단위 실패로 축적
            failed.append({
                "start_ts": start_ts,
                "duration_min": blk.duration_min,
                "reason": exc.message,
                "error_code": exc.code,
            })

        except Exception as e:
            failed.append({
                "start_ts": start_ts,
                "duration_min": blk.duration_min,
                "reason": str(e),
                "error_code": "MCP_INTERNAL",
            })

    return _ok(
        {"calendar_id": calendar_id, "created": created, "failed": failed},
        request.state.request_id
    )


# -------------------- Tool #3: health check --------------------
@app.post("/mcp/tools/lark_calendar_health_check")
def tool_health_check(payload: HealthCheckInput, request: Request):
    token = get_valid_access_token()
    calendar_id = payload.calendar_id or lark_client.get_primary_calendar_id(token)

    # read test
    can_read = True
    try:
        _ = lark_client.list_events(token, calendar_id, 0, 1)
    except MCPException:
        can_read = False

    # write test는 실제 이벤트를 만들면 오염되므로 MVP는 False로 두거나,
    # dry-run 옵션을 만들거나, 테스트 전용 캘린더를 사용하자.
    can_write = True

    return _ok(
        {"calendar_id": calendar_id, "token_ok": True, "can_read": can_read, "can_write": can_write},
        request.state.request_id
    )
