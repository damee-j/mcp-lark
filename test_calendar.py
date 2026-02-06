#!/usr/bin/env python3
"""
캘린더 조회 테스트 스크립트
"""
import json
from datetime import datetime, timedelta
from token_provider import get_valid_access_token
from lark_client import get_primary_calendar_id, list_events

def main():
    print("=" * 70)
    print("🧪 MCP Lark 캘린더 조회 테스트")
    print("=" * 70)

    # 1. 토큰 가져오기
    print("\n1️⃣ Access Token 확인...")
    try:
        token = get_valid_access_token()
        print(f"   ✅ Token: {token[:30]}...")
    except Exception as e:
        print(f"   ❌ 토큰 에러: {e}")
        return

    # 2. Primary 캘린더 ID 조회
    print("\n2️⃣ Primary 캘린더 ID 조회...")
    try:
        calendar_id = get_primary_calendar_id(token)
        print(f"   ✅ Calendar ID: {calendar_id}")
    except Exception as e:
        print(f"   ❌ 캘린더 조회 에러: {e}")
        return

    # 3. 오늘 일정 조회
    print("\n3️⃣ 오늘 일정 조회...")
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    start_ts = int(today_start.timestamp())
    end_ts = int(today_end.timestamp())

    print(f"   📅 조회 범위: {today_start.strftime('%Y-%m-%d %H:%M')} ~ {today_end.strftime('%Y-%m-%d %H:%M')}")

    try:
        events = list_events(token, calendar_id, start_ts, end_ts)
        print(f"   ✅ 일정 {len(events)}개 발견")
    except Exception as e:
        print(f"   ❌ 일정 조회 에러: {e}")
        return

    # 4. 데이터 구조 출력
    print("\n4️⃣ 데이터 구조 분석")
    print("   " + "=" * 66)

    if not events:
        print("   📭 오늘 일정이 없습니다.")
    else:
        for i, event in enumerate(events[:3], 1):  # 최대 3개만 출력
            print(f"\n   📆 일정 #{i}")
            print(f"   {'-' * 66}")

            # 주요 필드
            print(f"   event_id:       {event.get('event_id', 'N/A')}")
            print(f"   summary:        {event.get('summary', '(제목 없음)')}")

            # 시간 정보
            start_time = event.get('start_time', {})
            end_time = event.get('end_time', {})

            if 'timestamp' in start_time:
                start_dt = datetime.fromtimestamp(int(start_time['timestamp']))
                print(f"   시작 시간:      {start_dt.strftime('%Y-%m-%d %H:%M')}")

            if 'timestamp' in end_time:
                end_dt = datetime.fromtimestamp(int(end_time['timestamp']))
                print(f"   종료 시간:      {end_dt.strftime('%Y-%m-%d %H:%M')}")

                # 소요 시간 계산
                if 'timestamp' in start_time:
                    duration_min = (end_dt - start_dt).total_seconds() / 60
                    print(f"   소요 시간:      {int(duration_min)}분")

            # 기타 정보
            print(f"   종일 일정:      {event.get('is_all_day', False)}")
            print(f"   위치:           {event.get('location', 'N/A')}")
            print(f"   설명:           {event.get('description', 'N/A')[:50]}{'...' if len(event.get('description', '')) > 50 else ''}")
            print(f"   상태:           {event.get('status', 'N/A')}")

            # Organizer 정보
            organizer = event.get('organizer')
            if organizer and isinstance(organizer, dict):
                print(f"   주최자 이메일:  {organizer.get('email', 'N/A')}")
                print(f"   주최자 이름:    {organizer.get('name', 'N/A')}")

        if len(events) > 3:
            print(f"\n   ... 외 {len(events) - 3}개 일정 더 있음")

    # 5. 전체 JSON 구조 (첫 번째 일정만)
    if events:
        print("\n5️⃣ 첫 번째 일정의 전체 JSON 구조")
        print("   " + "=" * 66)
        print(json.dumps(events[0], indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("✅ 테스트 완료!")
    print("=" * 70)

if __name__ == "__main__":
    main()
