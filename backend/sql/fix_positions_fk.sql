-- positions 테이블의 foreign key를 profiles 테이블로 변경
-- 1. 기존 foreign key 삭제
ALTER TABLE positions 
DROP CONSTRAINT IF EXISTS positions_user_id_fkey;

-- 2. 새로운 foreign key 생성 (profiles 테이블 참조)
ALTER TABLE positions 
ADD CONSTRAINT positions_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES profiles(id) ON DELETE CASCADE;