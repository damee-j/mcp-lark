# Lark MCP Server

Lark Calendar API를 위한 MCP (Model Context Protocol) 서버입니다.

## 기능

1. **List Events** - 캘린더 이벤트 조회
2. **Create Focus Blocks** - Focus Block 일괄 생성
3. **Health Check** - 연결 및 권한 확인

## 특징

✅ **Tenant Access Token 자동 갱신** - OAuth 로그인 불필요
✅ **Railway 배포 최적화** - App ID + Secret만으로 작동
✅ **표준 에러 코드** - 명확한 에러 처리

## 로컬 개발

### 설치

```bash
pip install -r requirements.txt
```

### 환경변수 설정

`.env` 파일에 Lark App 정보 입력:

```bash
LARK_APP_ID=your_app_id
LARK_APP_SECRET=your_app_secret

# 선택적: 특정 캘린더 ID 지정
LARK_CALENDAR_ID=xxx@group.calendar.feishu.cn
```

### 서버 실행

```bash
uvicorn app:app --reload --port 8000
```

서버가 실행되면 http://localhost:8000 에서 접근할 수 있습니다.

### API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Railway 배포 🚀

### 1. GitHub에 푸시

```bash
cd /Users/damee/dev/my-first-skill/mcp_lark
git init
git add .
git commit -m "Initial commit: Lark MCP server"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Railway 프로젝트 생성

1. https://railway.com 접속
2. **New Project** 클릭
3. **Deploy from GitHub repo** 선택
4. 저장소 선택: `mcp_lark`

### 3. Environment Variables 설정

Railway 대시보드 → Variables 탭:

**필수:**
```
LARK_APP_ID=cli_a90ee729a4389eed
LARK_APP_SECRET=uW053LW5nhMOBloQoAgQze5aLFC54Syq
LARK_USER_TOKEN=your_oauth_token_here
```

**선택적:**
```
LARK_CALENDAR_ID=your_calendar_id@group.calendar.feishu.cn
```

**LARK_USER_TOKEN 발급 방법:**
1. 로컬에서 `python3 lark_oauth.py` 실행
2. 브라우저에서 Lark 로그인
3. `.env` 파일에서 `LARK_USER_TOKEN` 복사
4. Railway Variables에 붙여넣기

⚠️ **주의:** User Token은 약 30일 후 만료됩니다. 만료 시 다시 발급해야 합니다.

### 4. 자동 배포 완료!

Railway가 자동으로:
- Python 환경 감지
- `requirements.txt` 설치
- `Procfile` 읽고 서버 시작

배포 완료 후 URL: `https://your-app.railway.app`

## API 엔드포인트

### GET /health
서버 상태 확인

**Response:**
```json
{
  "ok": true,
  "data": {"status": "ok"},
  "request_id": "..."
}
```

### POST /mcp/tools/lark_calendar_list_events
캘린더 이벤트 목록 조회

**Request Body:**
```json
{
  "range_start_ts": 1704067200,
  "range_end_ts": 1704153600,
  "calendar_id": "optional_calendar_id"
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "calendar_id": "xxx@group.calendar.feishu.cn",
    "events": [
      {
        "event_id": "...",
        "summary": "Meeting",
        "start_ts": 1704088800,
        "end_ts": 1704092400,
        "is_all_day": false
      }
    ]
  },
  "request_id": "..."
}
```

### POST /mcp/tools/lark_calendar_create_focus_blocks
Focus Block 일괄 생성

**Request Body:**
```json
{
  "title": "Deep Work",
  "blocks": [
    {
      "start_ts": 1704088800,
      "duration_min": 120
    }
  ],
  "description": "Focus time for important work",
  "visibility": "private",
  "free_busy_status": "busy"
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "calendar_id": "xxx@group.calendar.feishu.cn",
    "created": [
      {
        "event_id": "...",
        "start_ts": 1704088800,
        "end_ts": 1704096000
      }
    ],
    "failed": []
  },
  "request_id": "..."
}
```

### POST /mcp/tools/lark_calendar_health_check
Lark 연결 및 권한 확인

**Request Body:**
```json
{
  "calendar_id": "optional_calendar_id"
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "calendar_id": "xxx@group.calendar.feishu.cn",
    "token_ok": true,
    "can_read": true,
    "can_write": true
  },
  "request_id": "..."
}
```

## 에러 코드

| 코드 | HTTP | 설명 |
|------|------|------|
| `MCP_INVALID_ARGUMENT` | 400 | 잘못된 요청 파라미터 |
| `LARK_AUTH_REQUIRED` | 401 | 인증 필요 |
| `LARK_PERMISSION_DENIED` | 403 | 권한 없음 |
| `CAL_TIME_RANGE_INVALID` | 400 | 잘못된 시간 범위 |
| `CAL_EVENT_CREATE_CONFLICT` | 409 | 이벤트 생성 충돌 |
| `LARK_RATE_LIMITED` | 429 | Rate limit 초과 |
| `MCP_INTERNAL` | 500 | 서버 내부 오류 |
| `LARK_UPSTREAM_ERROR` | 502 | Lark API 오류 |

## 문제 해결

### Tenant Token 갱신 실패
```bash
# 토큰 캐시 삭제
rm -rf ~/.daily-focus/tenant_token.json

# 서버 재시작 (자동 재발급)
```

### 캘린더 접근 불가
1. Lark App 권한 확인: `calendar:calendar` scope 필요
2. 캘린더 공유 확인: 봇을 캘린더 멤버로 추가했는지 확인

## 라이선스

MIT
