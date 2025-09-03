-- 모든 검색 관련 트리거와 함수 완전 정리 및 재생성
-- Supabase SQL Editor에서 실행

-- 1. 모든 관련 트리거 제거
DROP TRIGGER IF EXISTS update_posts_search_idx ON posts;
DROP TRIGGER IF EXISTS update_post_search ON posts;
DROP TRIGGER IF EXISTS update_search_vector ON posts;

-- 2. 모든 관련 함수 제거
DROP FUNCTION IF EXISTS posts_search_trigger();
DROP FUNCTION IF EXISTS update_post_search_vector();
DROP FUNCTION IF EXISTS update_search_vector_trigger();

-- 3. search_vector 컬럼이 있으면 제거
ALTER TABLE posts DROP COLUMN IF EXISTS search_vector;

-- 4. search_idx 컬럼이 없으면 추가
ALTER TABLE posts 
ADD COLUMN IF NOT EXISTS search_idx tsvector;

-- 5. 인덱스 재생성
DROP INDEX IF EXISTS posts_search_idx;
CREATE INDEX posts_search_idx ON posts USING gin(search_idx);

-- 6. 영어 simple 검색을 사용하는 새 트리거 함수 생성
CREATE OR REPLACE FUNCTION update_posts_search_idx() RETURNS trigger AS $$
BEGIN
    NEW.search_idx := 
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.content, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.summary, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. 트리거 생성
CREATE TRIGGER update_posts_search_idx 
    BEFORE INSERT OR UPDATE ON posts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_posts_search_idx();

-- 8. 기존 게시글 업데이트 (있다면)
UPDATE posts 
SET search_idx = 
    setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(content, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(summary, '')), 'C');

-- 9. 검색 함수도 수정 (만약 있다면)
CREATE OR REPLACE FUNCTION search_posts(search_query text)
RETURNS SETOF posts AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM posts
    WHERE search_idx @@ plainto_tsquery('simple', search_query)
    ORDER BY ts_rank(search_idx, plainto_tsquery('simple', search_query)) DESC;
END;
$$ LANGUAGE plpgsql;

-- 10. 성공 메시지
SELECT 'All search triggers and functions have been updated to use simple search' as status;