-- Step 1: 기본 테이블 생성 (외래키 없이)

-- Stocks table (종목 마스터)
CREATE TABLE IF NOT EXISTS stocks (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(20) CHECK (market IN ('KOSPI', 'KOSDAQ', 'KONEX')),
    sector VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Profiles table (사용자 프로필)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    kiwoom_account VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Market index table (시장 지수)
CREATE TABLE IF NOT EXISTS market_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_code VARCHAR(20) NOT NULL,
    index_name VARCHAR(100) NOT NULL,
    current_value DECIMAL(10, 2) NOT NULL,
    change_value DECIMAL(10, 2),
    change_rate DECIMAL(5, 2),
    trading_volume BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_code)
);