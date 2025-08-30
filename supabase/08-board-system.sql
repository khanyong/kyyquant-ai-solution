-- Step 8: 게시판 시스템 및 접근 권한

-- 게시판 카테고리 테이블
CREATE TABLE IF NOT EXISTS board_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    parent_id UUID REFERENCES board_categories(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 게시판 테이블
CREATE TABLE IF NOT EXISTS boards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES board_categories(id) ON DELETE SET NULL,
    code VARCHAR(50) UNIQUE NOT NULL, -- 게시판 고유 코드 (notice, free, qna, strategy 등)
    name VARCHAR(100) NOT NULL,
    description TEXT,
    board_type VARCHAR(50) DEFAULT 'general', -- general, notice, qna, strategy, analysis 등
    
    -- 접근 권한 설정
    read_permission VARCHAR(100) DEFAULT 'all', -- all, user, premium, admin 등
    write_permission VARCHAR(100) DEFAULT 'user',
    comment_permission VARCHAR(100) DEFAULT 'user',
    
    -- 게시판 옵션
    allow_anonymous BOOLEAN DEFAULT false,
    use_comment BOOLEAN DEFAULT true,
    use_like BOOLEAN DEFAULT true,
    use_attachment BOOLEAN DEFAULT true,
    max_attachment_size INTEGER DEFAULT 10485760, -- 10MB
    allowed_file_types JSONB DEFAULT '["jpg", "png", "pdf", "xlsx", "docx"]',
    
    -- 게시판 설정
    posts_per_page INTEGER DEFAULT 20,
    use_category BOOLEAN DEFAULT false,
    categories JSONB, -- 게시판별 카테고리 (예: ["분석", "전략", "뉴스"])
    
    -- 권한별 추가 설정
    min_role_level INTEGER DEFAULT 0, -- 최소 역할 레벨
    required_permissions JSONB DEFAULT '[]', -- 필요한 권한 목록
    excluded_roles JSONB DEFAULT '[]', -- 제외할 역할
    
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 게시글 테이블
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    board_id UUID REFERENCES boards(id) ON DELETE CASCADE,
    author_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    
    -- 게시글 내용
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    category VARCHAR(100), -- 게시판 내 카테고리
    tags JSONB DEFAULT '[]',
    
    -- 게시글 상태
    status VARCHAR(20) DEFAULT 'published', -- draft, published, hidden, deleted
    is_notice BOOLEAN DEFAULT false,
    is_pinned BOOLEAN DEFAULT false,
    is_secret BOOLEAN DEFAULT false,
    secret_password VARCHAR(255), -- 비밀글 비밀번호 (해시)
    
    -- 조회수 및 추천
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    dislike_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    -- 메타 정보
    ip_address INET,
    user_agent TEXT,
    
    published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- 전체 텍스트 검색을 위한 필드
    search_vector tsvector
);

-- 댓글 테이블
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE, -- 대댓글
    
    content TEXT NOT NULL,
    is_secret BOOLEAN DEFAULT false,
    
    like_count INTEGER DEFAULT 0,
    dislike_count INTEGER DEFAULT 0,
    
    ip_address INET,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 첨부파일 테이블
CREATE TABLE IF NOT EXISTS attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(100),
    mime_type VARCHAR(100),
    
    download_count INTEGER DEFAULT 0,
    
    uploaded_by UUID REFERENCES profiles(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (
        (post_id IS NOT NULL AND comment_id IS NULL) OR
        (post_id IS NULL AND comment_id IS NOT NULL)
    )
);

-- 좋아요/싫어요 테이블
CREATE TABLE IF NOT EXISTS reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    
    reaction_type VARCHAR(20) NOT NULL, -- like, dislike
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, post_id),
    UNIQUE(user_id, comment_id),
    CHECK (
        (post_id IS NOT NULL AND comment_id IS NULL) OR
        (post_id IS NULL AND comment_id IS NOT NULL)
    )
);

-- 게시판 접근 권한 테이블 (세부 권한 설정)
CREATE TABLE IF NOT EXISTS board_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    board_id UUID REFERENCES boards(id) ON DELETE CASCADE,
    role_name VARCHAR(50),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    can_read BOOLEAN DEFAULT true,
    can_write BOOLEAN DEFAULT false,
    can_comment BOOLEAN DEFAULT true,
    can_delete_own BOOLEAN DEFAULT true,
    can_delete_any BOOLEAN DEFAULT false,
    can_edit_own BOOLEAN DEFAULT true,
    can_edit_any BOOLEAN DEFAULT false,
    can_pin BOOLEAN DEFAULT false,
    can_notice BOOLEAN DEFAULT false,
    
    granted_by UUID REFERENCES profiles(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(board_id, role_name, user_id)
);

-- 기본 게시판 생성
INSERT INTO board_categories (name, display_name, description, sort_order) VALUES
    ('general', '일반', '일반 게시판', 1),
    ('trading', '트레이딩', '트레이딩 관련 게시판', 2),
    ('strategy', '전략', '투자 전략 게시판', 3),
    ('analysis', '분석', '시장 분석 게시판', 4),
    ('support', '지원', '고객 지원 게시판', 5)
ON CONFLICT (name) DO NOTHING;

INSERT INTO boards (code, name, category_id, board_type, description, read_permission, write_permission) VALUES
    ('notice', '공지사항', (SELECT id FROM board_categories WHERE name = 'general'), 'notice', 
     '시스템 공지사항', 'all', 'admin'),
    
    ('free', '자유게시판', (SELECT id FROM board_categories WHERE name = 'general'), 'general', 
     '자유로운 소통 공간', 'all', 'user'),
    
    ('qna', 'Q&A', (SELECT id FROM board_categories WHERE name = 'support'), 'qna', 
     '질문과 답변', 'all', 'user'),
    
    ('strategy_share', '전략 공유', (SELECT id FROM board_categories WHERE name = 'strategy'), 'strategy', 
     '투자 전략 공유', 'user', 'standard'),
    
    ('premium_strategy', '프리미엄 전략', (SELECT id FROM board_categories WHERE name = 'strategy'), 'strategy', 
     '프리미엄 회원 전용 전략', 'premium', 'premium'),
    
    ('market_analysis', '시장 분석', (SELECT id FROM board_categories WHERE name = 'analysis'), 'analysis', 
     '시장 분석 리포트', 'user', 'standard'),
    
    ('backtesting', '백테스트 결과', (SELECT id FROM board_categories WHERE name = 'analysis'), 'analysis', 
     '백테스트 결과 공유', 'user', 'user'),
    
    ('admin', '관리자 게시판', (SELECT id FROM board_categories WHERE name = 'general'), 'general', 
     '관리자 전용 게시판', 'admin', 'admin')
ON CONFLICT (code) DO NOTHING;

-- 게시판 접근 권한 확인 함수
CREATE OR REPLACE FUNCTION check_board_permission(
    p_user_id UUID,
    p_board_code VARCHAR,
    p_action VARCHAR -- read, write, comment, delete, edit, pin, notice
)
RETURNS BOOLEAN AS $$
DECLARE
    v_board boards%ROWTYPE;
    v_user_role VARCHAR(50);
    v_user_level INTEGER;
    v_has_permission BOOLEAN := false;
BEGIN
    -- 게시판 정보 가져오기
    SELECT * INTO v_board FROM boards WHERE code = p_board_code AND is_active = true;
    
    IF v_board IS NULL THEN
        RETURN false;
    END IF;
    
    -- 사용자 역할 및 레벨 가져오기
    SELECT role INTO v_user_role FROM profiles WHERE id = p_user_id;
    SELECT level INTO v_user_level FROM roles WHERE name = v_user_role;
    
    -- 액션별 권한 확인
    CASE p_action
        WHEN 'read' THEN
            IF v_board.read_permission = 'all' THEN
                RETURN true;
            ELSIF v_board.read_permission = v_user_role THEN
                RETURN true;
            ELSIF v_user_level >= v_board.min_role_level THEN
                RETURN true;
            END IF;
            
        WHEN 'write' THEN
            IF v_board.write_permission = 'all' AND p_user_id IS NOT NULL THEN
                RETURN true;
            ELSIF v_board.write_permission = v_user_role THEN
                RETURN true;
            ELSIF v_user_level >= v_board.min_role_level THEN
                RETURN true;
            END IF;
            
        WHEN 'comment' THEN
            IF v_board.comment_permission = 'all' AND p_user_id IS NOT NULL THEN
                RETURN true;
            ELSIF v_board.comment_permission = v_user_role THEN
                RETURN true;
            END IF;
            
        ELSE
            -- 특별 권한은 board_permissions 테이블 확인
            SELECT EXISTS (
                SELECT 1 FROM board_permissions
                WHERE board_id = v_board.id
                AND (user_id = p_user_id OR role_name = v_user_role)
                AND CASE p_action
                    WHEN 'delete' THEN can_delete_any
                    WHEN 'edit' THEN can_edit_any
                    WHEN 'pin' THEN can_pin
                    WHEN 'notice' THEN can_notice
                    ELSE false
                END = true
                AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            ) INTO v_has_permission;
    END CASE;
    
    RETURN v_has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 전체 텍스트 검색 인덱스
CREATE INDEX IF NOT EXISTS idx_posts_search ON posts USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_posts_board_status ON posts(board_id, status);
CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_attachments_post ON attachments(post_id);

-- 검색 벡터 업데이트 트리거
CREATE OR REPLACE FUNCTION update_post_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('korean', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('korean', COALESCE(NEW.content, '')), 'B') ||
        setweight(to_tsvector('korean', COALESCE(NEW.summary, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_post_search
    BEFORE INSERT OR UPDATE ON posts
    FOR EACH ROW
    EXECUTE FUNCTION update_post_search_vector();

-- RLS 정책
ALTER TABLE boards ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE reactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE board_permissions ENABLE ROW LEVEL SECURITY;

-- 게시판 RLS
CREATE POLICY "Anyone can view active boards" ON boards
    FOR SELECT USING (is_active = true);

CREATE POLICY "Admins can manage boards" ON boards
    FOR ALL USING (
        check_user_permission(auth.uid(), 'manage_boards')
    );

-- 게시글 RLS
CREATE POLICY "Users can view posts based on board permissions" ON posts
    FOR SELECT USING (
        check_board_permission(auth.uid(), 
            (SELECT code FROM boards WHERE id = board_id), 
            'read')
    );

CREATE POLICY "Users can create posts based on board permissions" ON posts
    FOR INSERT WITH CHECK (
        check_board_permission(auth.uid(), 
            (SELECT code FROM boards WHERE id = board_id), 
            'write')
    );

CREATE POLICY "Users can update own posts" ON posts
    FOR UPDATE USING (
        author_id = auth.uid() OR
        check_board_permission(auth.uid(), 
            (SELECT code FROM boards WHERE id = board_id), 
            'edit')
    );

CREATE POLICY "Users can delete own posts" ON posts
    FOR DELETE USING (
        author_id = auth.uid() OR
        check_board_permission(auth.uid(), 
            (SELECT code FROM boards WHERE id = board_id), 
            'delete')
    );