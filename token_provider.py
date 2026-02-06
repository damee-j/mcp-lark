from __future__ import annotations
import os
from dotenv import load_dotenv
from errors import auth_required

load_dotenv()


def get_valid_access_token() -> str:
    """
    User Access Token 사용 (개인 캘린더 접근):
    - 사용자의 개인 캘린더에 직접 접근 가능
    - OAuth 로그인으로 발급
    - 유효기간: 약 30일

    ⚠️ 주의: 토큰이 만료되면 다시 로그인 필요
    로컬: python3 lark_oauth.py
    Railway: 환경변수 LARK_USER_TOKEN 업데이트
    """
    token = os.getenv("LARK_USER_TOKEN")
    if not token:
        raise auth_required(
            "Missing LARK_USER_TOKEN in environment. "
            "Run: python3 lark_oauth.py"
        )
    return token


def get_bot_token() -> str:
    """
    Bot Token (선택적, 봇 메시징 등 특수 기능에 사용)
    """
    token = os.getenv("LARK_BOT_TOKEN")
    if not token:
        raise auth_required("Missing LARK_BOT_TOKEN in environment.")
    return token
