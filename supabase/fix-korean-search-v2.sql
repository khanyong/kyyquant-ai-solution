-- 한국어 텍스트 검색 설정 문제 해결 (search_idx 컬럼 추가 포함)
-- Supabase SQL Editor에서 실행

-- 1. 기존 트리거 제거
DROP TRIGGER IF EXISTS update_posts_search_idx ON posts;

-- 2. 기존 함수 제거
DROP FUNCTION IF EXISTS posts_search_trigger();

-- 3. search_idx 컬럼이 없으면 추가
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS search_idx tsvector;

-- 4. 인덱스 생성 (이미 있으면 무시)
CREATE INDEX IF NOT EXISTS posts_search_idx 
ON posts USING gin(search_idx);

-- 5. 간단한 검색으로 대체하는 트리거 함수 생성
CREATE OR REPLACE FUNCTION posts_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_idx := 
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.content, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.summary, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. 트리거 재생성
CREATE TRIGGER update_posts_search_idx 
    BEFORE INSERT OR UPDATE ON posts 
    FOR EACH ROW 
    EXECUTE FUNCTION posts_search_trigger();

-- 7. 기존 게시글의 search_idx 업데이트
UPDATE posts 
SET search_idx = 
    setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(content, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(summary, '')), 'C')
WHERE search_idx IS NULL;

-- 8. 성공 메시지
SELECT 'Search index column added and configured' as status;