# Edge Function 로그 확인 방법

## 1. Supabase Dashboard 접속
https://supabase.com/dashboard/project/hznkyaomtrpzcayayayh

## 2. Edge Functions 메뉴 이동
- 좌측 메뉴에서 "Edge Functions" 클릭

## 3. sync-kiwoom-balance 함수 선택
- 함수 목록에서 "sync-kiwoom-balance" 클릭

## 4. Logs 탭 확인
- "Logs" 탭 클릭
- 최근 실행 로그 확인
- 에러 메시지가 있는지 확인

## 5. 확인할 내용
- 함수가 실행되었는지 (200 OK vs 400/500 Error)
- 토큰 발급 성공 여부
- API 호출 결과
- 에러 메시지

## 6. 수동 테스트
또는 다음 명령으로 수동 호출 테스트:

```bash
curl -X POST \
  https://hznkyaomtrpzcayayayh.supabase.co/functions/v1/sync-kiwoom-balance \
  -H "Authorization: Bearer [YOUR_ANON_KEY]" \
  -H "Content-Type: application/json"
```

---

**대체 방법: 프론트엔드 코드에서 호출 확인**

UI 코드에서 Edge Function을 어떻게 호출하는지 확인해야 합니다.
