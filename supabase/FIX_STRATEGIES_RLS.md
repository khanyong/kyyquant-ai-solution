# strategies 테이블 RLS 정책 수정 가이드

## 문제 상황
- admin이 아닌 사용자가 전략을 저장할 수 없는 문제 발생
- 원인 1: strategies 테이블의 RLS 정책이 잘못 설정됨 (모든 사용자에게 true로 설정)
- 원인 2: 클라이언트 코드에서 user_id가 없을 때 하드코딩된 UUID 사용

## 해결 방법

### 1. 클라이언트 코드 수정 (완료)
- `src/components/StrategyBuilder.tsx` 파일 수정
  - 587번째 줄: 하드코딩된 UUID 제거
  - 로그인하지 않은 사용자에 대한 에러 처리 추가

### 2. Supabase RLS 정책 수정 (필요)

#### Supabase Dashboard에서 직접 수정하는 방법:

1. [Supabase Dashboard](https://app.supabase.com) 로그인
2. 프로젝트 선택
3. 왼쪽 메뉴에서 "Authentication" → "Policies" 선택
4. `strategies` 테이블 찾기
5. 기존 정책 삭제:
   - "Enable all for strategies based on user_id" 정책 삭제

6. 새로운 정책 추가:
   ```sql
   -- SELECT 정책
   CREATE POLICY "Users can view own strategies" ON strategies
       FOR SELECT 
       USING (auth.uid() = user_id);

   -- INSERT 정책
   CREATE POLICY "Users can create own strategies" ON strategies
       FOR INSERT 
       WITH CHECK (auth.uid() = user_id);

   -- UPDATE 정책
   CREATE POLICY "Users can update own strategies" ON strategies
       FOR UPDATE 
       USING (auth.uid() = user_id)
       WITH CHECK (auth.uid() = user_id);

   -- DELETE 정책
   CREATE POLICY "Users can delete own strategies" ON strategies
       FOR DELETE 
       USING (auth.uid() = user_id);
   ```

#### SQL Editor에서 수정하는 방법:

1. Supabase Dashboard → SQL Editor
2. `fix-strategies-rls-policy.sql` 파일의 내용 복사
3. 실행

## 테스트 방법

1. admin이 아닌 일반 사용자로 로그인
2. 전략 빌더에서 새 전략 생성
3. "저장" 버튼 클릭
4. 성공적으로 저장되는지 확인
5. "불러오기"로 자신의 전략만 보이는지 확인

## 추가 고려사항

### Admin 사용자를 위한 정책 (선택사항)
admin 역할을 가진 사용자가 모든 전략을 볼 수 있도록 하려면:

```sql
CREATE POLICY "Admins can view all strategies" ON strategies
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );
```

## 롤백 방법

문제가 발생한 경우 원래 정책으로 되돌리기:

```sql
-- 새 정책 삭제
DROP POLICY IF EXISTS "Users can view own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can create own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can update own strategies" ON strategies;
DROP POLICY IF EXISTS "Users can delete own strategies" ON strategies;

-- 원래 정책 복원 (임시)
CREATE POLICY "Enable all for strategies based on user_id" ON strategies
    FOR ALL USING (true);
```

## 확인 사항

- [ ] 클라이언트 코드 수정 완료
- [ ] Supabase RLS 정책 업데이트
- [ ] 일반 사용자로 테스트
- [ ] Admin 사용자로 테스트