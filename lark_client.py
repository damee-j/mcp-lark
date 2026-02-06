from __future__ import annotations
import os
import requests
from typing import Any, Dict, List, Optional
from errors import (
    auth_required, permission_denied, rate_limited, upstream_error, internal_error
)
from token_provider import get_valid_access_token

LARK_BASE = "https://open.larksuite.com/open-apis"

def _handle_lark_response(resp: requests.Response) -> Dict[str, Any]:
    # HTTP 레벨
    if resp.status_code == 401:
        raise auth_required("Lark token invalid or expired.")
    if resp.status_code == 403:
        raise permission_denied("Lark permission denied.")
    if resp.status_code == 429:
        raise rate_limited("Lark rate limited.")
    if 500 <= resp.status_code <= 599:
        raise upstream_error(f"Lark upstream error: {resp.status_code}")

    try:
        data = resp.json()
    except Exception as e:
        raise internal_error("Failed to parse Lark response JSON.", {"exception": str(e)})

    # Lark API envelope: code == 0 성공(일반적으로)
    if isinstance(data, dict) and data.get("code") not in (0, None):
        # code != 0 이면 Lark 내부 에러
        # code/ msg 구조는 API마다 조금 다를 수 있어 안전하게 처리
        msg = data.get("msg") or data.get("message") or "Lark API error"
        # 인증/권한류 추정
        if "auth" in msg.lower():
            raise auth_required(msg, {"lark_code": data.get("code")})
        raise upstream_error(msg, {"lark_code": data.get("code"), "raw": data})

    return data


def get_primary_calendar_id(access_token: str) -> str:
    # 1. 환경변수에서 먼저 확인 (수동 설정된 캘린더 ID)
    env_calendar_id = os.getenv("LARK_CALENDAR_ID")
    if env_calendar_id:
        return env_calendar_id

    # 2. API로 캘린더 목록 조회
    url = f"{LARK_BASE}/calendar/v4/calendars"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=15)
    data = _handle_lark_response(resp)

    items = (((data.get("data") or {}).get("calendar_list")) or [])
    # primary 찾기
    for cal in items:
        if cal.get("type") == "primary":
            cid = cal.get("calendar_id")
            if cid:
                return cid

    # fallback: 첫 번째
    if items and items[0].get("calendar_id"):
        return items[0]["calendar_id"]

    raise upstream_error("No calendar_id found from Lark. Set LARK_CALENDAR_ID in .env file.")


def list_events(access_token: str, calendar_id: str, start_ts: int, end_ts: int) -> List[Dict[str, Any]]:
    url = f"{LARK_BASE}/calendar/v4/calendars/{calendar_id}/events"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "start_time": str(start_ts),
        "end_time": str(end_ts),
        "page_size": "200"
    }
    resp = requests.get(url, headers=headers, params=params, timeout=20)
    data = _handle_lark_response(resp)

    events = (((data.get("data") or {}).get("items")) or [])
    return events


def create_event(
    access_token: str,
    calendar_id: str,
    summary: str,
    start_ts: int,
    end_ts: int,
    description: str,
    visibility: str = "private",
    free_busy_status: str = "busy",
) -> str:
    url = f"{LARK_BASE}/calendar/v4/calendars/{calendar_id}/events"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    payload = {
        "summary": summary,
        "description": description,
        "visibility": visibility,
        "free_busy_status": free_busy_status,
        "start_time": {"timestamp": str(start_ts)},
        "end_time": {"timestamp": str(end_ts)},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    data = _handle_lark_response(resp)

    evt = (((data.get("data") or {}).get("event")) or {})
    event_id = evt.get("event_id")
    if not event_id:
        raise upstream_error("Lark create_event succeeded but event_id missing.", {"raw": data})
    return event_id
