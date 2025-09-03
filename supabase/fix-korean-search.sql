-- 한국어 텍스트 검색 설정 문제 해결
-- Supabase SQL Editor에서 실행

-- 1. 기존 트리거 제거
DROP TRIGGER IF EXISTS update_posts_search_idx ON posts;

-- 2. 기존 함수 제거
DROP FUNCTION IF EXISTS posts_search_trigger();

-- 3. 간단한 영어 검색으로 대체하는 트리거 함수 생성
CREATE OR REPLACE FUNCTION posts_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_idx := 
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.content, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.summary, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. 트리거 재생성
CREATE TRIGGER update_posts_search_idx 
    BEFORE INSERT OR UPDATE ON posts 
    FOR EACH ROW 
    EXECUTE FUNCTION posts_search_trigger();

-- 5. 기존 게시글의 search_idx 업데이트
UPDATE posts 
SET search_idx = 
    setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(content, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(summary, '')), 'C');

-- 6. 성공 메시지
SELECT 'Korean search configuration replaced with simple search' as status;