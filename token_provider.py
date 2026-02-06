from __future__ import annotations
import os
from dotenv import load_dotenv
from errors import auth_required
from lark_tenant_token import get_valid_tenant_token

load_dotenv()


def get_valid_access_token() -> str:
    """
    Tenant Access Token 사용 (자동 갱신):
    - App ID + App Secret만으로 자동 갱신
    - 2시간마다 자동 갱신 (캐시 저장)
    - OAuth 로그인 불필요
    - Railway 배포에 최적화

    ⚠️ 주의: Tenant Token은 앱 권한으로 작동합니다.
    개인 캘린더를 사용하려면 Lark에서 캘린더를 봇과 공유하세요.
    """
    try:
        return get_valid_tenant_token()
    except Exception as e:
        raise auth_required(f"Failed to get tenant access token: {str(e)}")


def get_bot_token() -> str:
    """
    Bot Token (선택적, 봇 메시징 등 특수 기능에 사용)
    """
    token = os.getenv("LARK_BOT_TOKEN")
    if not token:
        raise auth_required("Missing LARK_BOT_TOKEN in environment.")
    return token
