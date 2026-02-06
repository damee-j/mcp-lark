#!/usr/bin/env python3
"""
오늘 일정을 시간순으로 깔끔하게 출력
"""
from datetime import datetime, timedelta
from token_provider import get_valid_access_token
from lark_client import get_primary_calendar_id, list_events

def format_time(timestamp_str):
    """Unix timestamp를 HH:MM 형식으로 변환"""
    if not timestamp_str:
        return "시간 미정"
    dt = datetime.fromtimestamp(int(timestamp_str))
    return dt.strftime("%H:%M")

def main():
    print("=" * 80)
    print(f"📅 오늘 일정 ({datetime.now().strftime('%Y년 %m월 %d일 %A')})")
    print("=" * 80)

    # 토큰 및 캘린더 ID
    token = get_valid_access_token()
    calendar_id = get_primary_calendar_id(token)

    # 오늘 범위
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # 일정 조회
    events = list_events(
        token,
        calendar_id,
        int(today_start.timestamp()),
        int(today_end.timestamp())
    )

    if not events:
        print("\n📭 오늘은 일정이 없습니다.")
        return

    # 시간순 정렬
    def get_start_ts(event):
        start = event.get('start_time', {})
        return int(start.get('timestamp', 0))

    events.sort(key=get_start_ts)

    print(f"\n총 {len(events)}개 일정\n")

    # 시간대별 그룹핑
    current_time = datetime.now()
    past_events = []
    ongoing_events = []
    upcoming_events = []

    for event in events:
        start_ts = int(event.get('start_time', {}).get('timestamp', 0))
        end_ts = int(event.get('end_time', {}).get('timestamp', 0))

        start_dt = datetime.fromtimestamp(start_ts)
        end_dt = datetime.fromtimestamp(end_ts)

        if end_dt < current_time:
            past_events.append(event)
        elif start_dt <= current_time <= end_dt:
            ongoing_events.append(event)
        else:
            upcoming_events.append(event)

    # 진행 중인 일정
    if ongoing_events:
        print("⏰ 지금 진행 중")
        print("-" * 80)
        for event in ongoing_events:
            start = event.get('start_time', {})
            end = event.get('end_time', {})
            summary = event.get('summary', '(제목 없음)')

            start_time = format_time(start.get('timestamp'))
            end_time = format_time(end.get('timestamp'))

            print(f"  🔴 {start_time} - {end_time}  {summary}")
        print()

    # 다가올 일정
    if upcoming_events:
        print("📆 예정된 일정")
        print("-" * 80)
        for event in upcoming_events:
            start = event.get('start_time', {})
            end = event.get('end_time', {})
            summary = event.get('summary', '(제목 없음)')

            start_time = format_time(start.get('timestamp'))
            end_time = format_time(end.get('timestamp'))

            # Focus Block 표시
            icon = "🔒" if "🔒" in summary else "  "

            # 시간까지 남은 시간
            start_dt = datetime.fromtimestamp(int(start.get('timestamp')))
            time_left = start_dt - current_time
            hours_left = int(time_left.total_seconds() / 3600)
            minutes_left = int((time_left.total_seconds() % 3600) / 60)

            if hours_left > 0:
                time_info = f"({hours_left}시간 {minutes_left}분 후)"
            else:
                time_info = f"({minutes_left}분 후)"

            print(f"  {icon} {start_time} - {end_time}  {summary}  {time_info}")
        print()

    # 지난 일정
    if past_events:
        print(f"✅ 완료된 일정 ({len(past_events)}개)")
        print("-" * 80)
        for event in past_events[:5]:  # 최대 5개만
            start = event.get('start_time', {})
            end = event.get('end_time', {})
            summary = event.get('summary', '(제목 없음)')

            start_time = format_time(start.get('timestamp'))
            end_time = format_time(end.get('timestamp'))

            print(f"  ✓  {start_time} - {end_time}  {summary}")

        if len(past_events) > 5:
            print(f"     ... 외 {len(past_events) - 5}개")
        print()

    print("=" * 80)

if __name__ == "__main__":
    main()
