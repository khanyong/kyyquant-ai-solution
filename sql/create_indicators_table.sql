-- indicators 테이블 생성
-- 지표 정의와 계산 로직을 저장하는 테이블

-- 기존 테이블이 있으면 삭제 (주의: 데이터 손실)
-- DROP TABLE IF EXISTS indicators;

-- indicators 테이블 생성
CREATE TABLE IF NOT EXISTS indicators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,  -- 지표 이름 (소문자): 'macd', 'rsi', 'ma' 등
  display_name TEXT NOT NULL,  -- 표시 이름: 'MACD', 'RSI', '이동평균' 등
  description TEXT,  -- 지표 설명
  category TEXT,  -- 카테고리: 'trend', 'momentum', 'volatility', 'volume'
  calculation_type TEXT NOT NULL,  -- 계산 타입: 'built-in', 'custom_formula', 'python_code'
  formula JSONB,  -- 계산 공식, 파라미터, 또는 Python 코드
  default_params JSONB,  -- 기본 파라미터
  required_data TEXT[],  -- 필요한 데이터 컬럼: ['close'], ['high', 'low', 'close'] 등
  output_columns TEXT[],  -- 출력 컬럼명: ['ma_20'], ['macd_line', 'macd_signal', 'macd_hist']
  is_active BOOLEAN DEFAULT true,  -- 활성화 여부
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_indicators_name ON indicators(name);
CREATE INDEX idx_indicators_category ON indicators(category);
CREATE INDEX idx_indicators_is_active ON indicators(is_active);

-- RLS (Row Level Security) 활성화
ALTER TABLE indicators ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽을 수 있도록 정책 설정
CREATE POLICY "Allow public read access" ON indicators
  FOR SELECT USING (true);

-- 인증된 사용자만 수정 가능
CREATE POLICY "Allow authenticated users to insert" ON indicators
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update" ON indicators
  FOR UPDATE USING (auth.role() = 'authenticated');

-- 트리거: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_indicators_updated_at
  BEFORE UPDATE ON indicators
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- 코멘트 추가
COMMENT ON TABLE indicators IS '기술적 지표 정의 테이블';
COMMENT ON COLUMN indicators.name IS '지표 이름 (유니크, 소문자)';
COMMENT ON COLUMN indicators.calculation_type IS 'built-in: 내장 함수, custom_formula: 수식, python_code: Python 코드';
COMMENT ON COLUMN indicators.formula IS '계산 로직 (JSON 형식)';
COMMENT ON COLUMN indicators.default_params IS '기본 파라미터 설정';