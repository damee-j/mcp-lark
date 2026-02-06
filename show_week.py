#!/usr/bin/env python3
"""
이번 주 일정을 날짜별로 보기
"""
from datetime import datetime, timedelta
from token_provider import get_valid_access_token
from lark_client import get_primary_calendar_id, list_events

def main():
    # 토큰 및 캘린더 ID
    token = get_valid_access_token()
    calendar_id = get_primary_calendar_id(token)

    # 이번 주 월요일 ~ 일요일
    today = datetime.now()
    weekday = today.weekday()  # 0=월, 6=일

    monday = today - timedelta(days=weekday)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=7)

    print("=" * 80)
    print(f"📅 이번 주 일정 ({monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')})")
    print("=" * 80)

    # 일정 조회
    events = list_events(
        token,
        calendar_id,
        int(monday.timestamp()),
        int(sunday.timestamp())
    )

    print(f"\n총 {len(events)}개 일정\n")

    # 날짜별로 그룹핑
    from collections import defaultdict
    events_by_date = defaultdict(list)

    for event in events:
        start_ts = int(event.get('start_time', {}).get('timestamp', 0))
        if start_ts == 0:
            continue

        start_dt = datetime.fromtimestamp(start_ts)
        date_key = start_dt.strftime('%Y-%m-%d')
        events_by_date[date_key].append(event)

    # 날짜별 출력
    current_date = monday
    for day_offset in range(7):
        date = current_date + timedelta(days=day_offset)
        date_key = date.strftime('%Y-%m-%d')
        day_name = ['월', '화', '수', '목', '금', '토', '일'][date.weekday()]

        # 오늘 표시
        is_today = date.date() == today.date()
        today_mark = " ← 오늘" if is_today else ""

        print(f"\n{date.strftime('%m/%d')} ({day_name}){today_mark}")
        print("-" * 80)

        day_events = events_by_date.get(date_key, [])

        if not day_events:
            print("  📭 일정 없음")
        else:
            # 시간순 정렬
            day_events.sort(key=lambda e: int(e.get('start_time', {}).get('timestamp', 0)))

            for event in day_events:
                start = event.get('start_time', {})
                end = event.get('end_time', {})
                summary = event.get('summary', '(제목 없음)')

                start_dt = datetime.fromtimestamp(int(start.get('timestamp')))
                end_dt = datetime.fromtimestamp(int(end.get('timestamp')))

                start_time = start_dt.strftime('%H:%M')
                end_time = end_dt.strftime('%H:%M')

                # Focus Block 표시
                icon = "🔒" if "🔒" in summary else "  "

                # 소요 시간
                duration_min = int((end_dt - start_dt).total_seconds() / 60)

                print(f"  {icon} {start_time}-{end_time} ({duration_min}분)  {summary}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
