# Lark Calendar API 데이터 구조

mcp_lark가 조회하는 Lark Calendar API의 전체 데이터 구조 정리.

## 📋 Event 객체 필드

### 기본 정보
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `event_id` | string | 이벤트 고유 ID (예: `3430be1f-29bc-48b4-a9eb-87c97653f4d2_0`) | ✅ (삭제 시) |
| `summary` | string | 일정 제목 | ✅ |
| `description` | string | 일정 설명 | ✅ (Focus Block) |
| `status` | enum | `confirmed`, `tentative`, `cancelled` | ❌ |
| `color` | int | 캘린더 색상 코드 | ❌ |

### 시간 정보
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `start_time.timestamp` | string | 시작 시간 (Unix 초) | ✅ |
| `start_time.timezone` | string | 시작 시간대 (예: `Asia/Seoul`) | ❌ |
| `end_time.timestamp` | string | 종료 시간 (Unix 초) | ✅ |
| `end_time.timezone` | string | 종료 시간대 | ❌ |
| `create_time` | string | 생성 시간 (Unix 초) | ❌ |

### 반복 및 예외
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `recurrence` | string | RRULE 반복 규칙 (예: `FREQ=WEEKLY;INTERVAL=2;BYDAY=WE`) | ❌ |
| `is_exception` | boolean | 반복 일정의 예외 인스턴스 여부 | ❌ |

### 참석자 및 주최자
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `event_organizer.display_name` | string | 주최자 이름 | ❌ |
| `event_organizer.user_id` | string | 주최자 Lark User ID | ❌ |
| `organizer_calendar_id` | string | 주최자 캘린더 ID | ❌ |
| `attendee_ability` | string | 참석자 권한 (예: `can_invite_others`) | ❌ |

### 가시성 및 상태
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `visibility` | enum | `default`, `public`, `private` | ✅ (Focus Block은 `private`) |
| `free_busy_status` | enum | `busy`, `free` | ✅ (Focus Block은 `busy`) |

### 화상회의
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `vchat.meeting_url` | string | 화상회의 링크 (예: Lark VC) | ❌ |
| `vchat.vc_type` | string | 화상회의 타입 (예: `vc`) | ❌ |

### 알림
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `reminders` | array | 알림 설정 (예: `[{"minutes": 5}]`) | ❌ |

### 기타
| 필드 | 타입 | 설명 | daily-focus 사용 |
|------|------|------|------------------|
| `app_link` | string | Lark 앱 딥링크 | ❌ |
| `location` | string | 장소 | ❌ |

## 📦 전체 JSON 예시

```json
{
  "event_id": "3430be1f-29bc-48b4-a9eb-87c97653f4d2_0",
  "summary": "bi-weekly Product&HR",
  "description": "",
  "status": "confirmed",
  "color": -1,

  "start_time": {
    "timestamp": "1764723600",
    "timezone": "Asia/Seoul"
  },
  "end_time": {
    "timestamp": "1764725400",
    "timezone": "Asia/Seoul"
  },
  "create_time": "1763366905",

  "recurrence": "FREQ=WEEKLY;UNTIL=20260219T145959Z;INTERVAL=2;WKST=SU;BYDAY=WE",
  "is_exception": false,

  "event_organizer": {
    "display_name": "Sinki Kang(강신기)",
    "user_id": "ou_ea27c6efaf4836ce8c43c668e6e94ab8"
  },
  "organizer_calendar_id": "feishu.cn_kTIzmBy1DaFDRMcF15hN2f@group.calendar.feishu.cn",
  "attendee_ability": "can_invite_others",

  "visibility": "default",
  "free_busy_status": "busy",

  "vchat": {
    "meeting_url": "https://vc-sg.larksuite.com/j/568169883",
    "vc_type": "vc"
  },

  "reminders": [
    {"minutes": 5}
  ],

  "app_link": "https://applink.larksuite.com/client/calendar/event/detail?calendarId=7570936757828849378&key=3430be1f-29bc-48b4-a9eb-87c97653f4d2&originalTime=0&startTime=1764723600"
}
```

## 🔄 mcp_lark vs daily-focus 비교

### 동일하게 사용하는 필드
- ✅ `event_id` (삭제 시)
- ✅ `summary` (제목)
- ✅ `start_time.timestamp`, `end_time.timestamp` (시간)
- ✅ `description` (Focus Block 설명)
- ✅ `visibility` (private)
- ✅ `free_busy_status` (busy)

### mcp_lark만 지원 (추가 활용 가능)
- `recurrence` - 반복 일정 패턴 분석
- `event_organizer` - 주최자 필터링
- `vchat.meeting_url` - 화상회의 링크 추출
- `reminders` - 알림 설정 활용
- `app_link` - Lark 앱에서 바로 열기

## 🎯 활용 예시

### 1. Focus Block 필터링
```python
focus_blocks = [e for e in events if "🔒" in e.get("summary", "")]
```

### 2. 반복 일정 감지
```python
recurring_events = [e for e in events if e.get("recurrence")]
```

### 3. 화상회의 있는 일정
```python
vc_meetings = [e for e in events if e.get("vchat", {}).get("meeting_url")]
```

### 4. 다른 사람이 주최한 일정
```python
others_events = [e for e in events if e.get("event_organizer", {}).get("user_id") != my_user_id]
```
