"""
kw_financial_snapshot 테이블 생성
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
print("📡 Supabase 연결 중...")
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

# SQL 실행
create_table_sql = """
CREATE TABLE IF NOT EXISTS kw_financial_snapshot (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    market VARCHAR(20),
    snapshot_date DATE NOT NULL,
    snapshot_time TIME,
    
    -- 시가총액 (억원)
    market_cap BIGINT,
    shares_outstanding BIGINT,
    
    -- 가치평가 지표
    per DECIMAL(10,2),
    pbr DECIMAL(10,2),
    eps INTEGER,
    bps INTEGER,
    
    -- 수익성 지표
    roe DECIMAL(10,2),
    
    -- 가격 정보
    current_price INTEGER,
    change_rate DECIMAL(5,2),
    high_52w INTEGER,
    low_52w INTEGER,
    
    -- 거래 정보
    volume BIGINT,
    trading_value BIGINT,
    foreign_ratio DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# 인덱스 생성
create_index_sql = """
CREATE INDEX IF NOT EXISTS idx_stock_snapshot 
ON kw_financial_snapshot(stock_code, snapshot_date DESC);
"""

print("\n⚠️  이 작업은 Supabase 대시보드에서 수행해야 합니다.")
print("\n다음 단계를 따라주세요:")
print("\n1. Supabase 대시보드 열기:")
print("   https://supabase.com/dashboard/project/hznkyaomtrpzcayayayh")
print("\n2. SQL Editor 메뉴 클릭")
print("\n3. 아래 SQL 복사하여 실행:")
print("\n" + "="*60)
print(create_table_sql)
print(create_index_sql)
print("="*60)
print("\n4. 'Run' 버튼 클릭하여 실행")
print("\n테이블 생성 후 다시 데이터 수집을 실행하세요!")