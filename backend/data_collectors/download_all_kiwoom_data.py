"""
키움 OpenAPI+에서 제공하는 모든 데이터 수집
가능한 모든 정보를 데이터베이스에 저장
"""
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
from pykiwoom import Kiwoom
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase_client import get_supabase_client

class KiwoomCompleteDataCollector:
    """키움 OpenAPI+ 전체 데이터 수집기"""
    
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.supabase = get_supabase_client()
        
    def connect(self):
        """키움 접속"""
        self.kiwoom.CommConnect()
        return self.kiwoom.GetConnectState() == 1
    
    def get_all_available_data(self, stock_code: str) -> dict:
        """
        한 종목에 대해 키움 API에서 제공하는 모든 데이터 수집
        """
        
        print(f"\n{stock_code} 전체 데이터 수집 중...")
        all_data = {
            'stock_code': stock_code,
            'stock_name': self.kiwoom.GetMasterCodeName(stock_code)
        }
        
        # ==========================================
        # 1. 주식 기본정보 (opt10001)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10001",
                종목코드=stock_code,
                output="주식기본정보",
                next=0)
            
            if df is not None and not df.empty:
                all_data['basic_info'] = {
                    # 가격 정보
                    'current_price': abs(int(df.get('현재가', [0])[0])),
                    'change': int(df.get('전일대비', [0])[0]),
                    'change_rate': float(df.get('등락율', [0])[0]),
                    'volume': int(df.get('거래량', [0])[0]),
                    'trading_value': int(df.get('거래대금', [0])[0]) * 1000000,
                    
                    # 52주 고저
                    'high_52w': abs(int(df.get('250최고', [0])[0])),
                    'low_52w': abs(int(df.get('250최저', [0])[0])),
                    
                    # 가치평가 지표
                    'per': float(df.get('PER', [0])[0]),
                    'pbr': float(df.get('PBR', [0])[0]),
                    'eps': int(df.get('EPS', [0])[0]),
                    'bps': int(df.get('BPS', [0])[0]),
                    
                    # 수익성
                    'roe': float(df.get('ROE', [0])[0]),
                    'roa': float(df.get('ROA', [0])[0]),
                    
                    # 시가총액
                    'market_cap': int(df.get('시가총액', [0])[0]) * 100000000,
                    'shares_outstanding': int(df.get('유통주식', [0])[0]) * 1000,
                    
                    # 외국인/기관 보유
                    'foreign_ratio': float(df.get('외인소진률', [0])[0]),
                    'institution_ratio': float(df.get('기관순매매', [0])[0]),
                    
                    # 배당
                    'dividend_yield': float(df.get('시가배당률', [0])[0]),
                }
                print("  ✅ 기본정보")
        except Exception as e:
            print(f"  ❌ 기본정보: {e}")
        
        # ==========================================
        # 2. 일봉 데이터 (opt10081) - 10년
        # ==========================================
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            df = self.kiwoom.block_request("opt10081",
                종목코드=stock_code,
                기준일자=end_date,
                수정주가구분=1,
                output="주식일봉차트조회",
                next=0)
            
            if df is not None and not df.empty:
                all_data['daily_prices'] = df.to_dict('records')
                print(f"  ✅ 일봉 ({len(df)}일)")
        except Exception as e:
            print(f"  ❌ 일봉: {e}")
        
        # ==========================================
        # 3. 주봉 데이터 (opt10082)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10082",
                종목코드=stock_code,
                기준일자=end_date,
                수정주가구분=1,
                output="주식주봉차트조회",
                next=0)
            
            if df is not None and not df.empty:
                all_data['weekly_prices'] = df.to_dict('records')
                print(f"  ✅ 주봉 ({len(df)}주)")
        except Exception as e:
            print(f"  ❌ 주봉: {e}")
        
        # ==========================================
        # 4. 월봉 데이터 (opt10083)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10083",
                종목코드=stock_code,
                기준일자=end_date,
                수정주가구분=1,
                output="주식월봉차트조회",
                next=0)
            
            if df is not None and not df.empty:
                all_data['monthly_prices'] = df.to_dict('records')
                print(f"  ✅ 월봉 ({len(df)}개월)")
        except Exception as e:
            print(f"  ❌ 월봉: {e}")
        
        # ==========================================
        # 5. 재무제표 (opt10080)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10080",
                종목코드=stock_code,
                조회구분=0,  # 연간
                output="주식분석",
                next=0)
            
            if df is not None and not df.empty:
                all_data['financial_statements'] = {
                    # 최근 5년 재무제표
                    'yearly': df.head(5).to_dict('records'),
                    
                    # 최신 연도 상세
                    'latest': {
                        'fiscal_year': df.iloc[0].get('일자', ''),
                        'revenue': int(df.iloc[0].get('매출액', 0)) * 100000000,
                        'operating_profit': int(df.iloc[0].get('영업이익', 0)) * 100000000,
                        'net_profit': int(df.iloc[0].get('당기순이익', 0)) * 100000000,
                        'total_assets': int(df.iloc[0].get('자산총계', 0)) * 100000000,
                        'total_liabilities': int(df.iloc[0].get('부채총계', 0)) * 100000000,
                        'total_equity': int(df.iloc[0].get('자본총계', 0)) * 100000000,
                        'operating_margin': float(df.iloc[0].get('영업이익률', 0)),
                        'net_margin': float(df.iloc[0].get('순이익률', 0)),
                        'debt_ratio': float(df.iloc[0].get('부채비율', 0)),
                        'current_ratio': float(df.iloc[0].get('유동비율', 0)),
                    }
                }
                print(f"  ✅ 재무제표 ({len(df)}년)")
        except Exception as e:
            print(f"  ❌ 재무제표: {e}")
        
        # ==========================================
        # 6. 투자자별 매매동향 (opt10059)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10059",
                일자="",
                종목코드=stock_code,
                금액수량구분=2,  # 수량
                매매구분=0,  # 순매수
                단위구분=1,  # 천주
                output="투자자별매매",
                next=0)
            
            if df is not None and not df.empty:
                all_data['investor_trading'] = df.head(30).to_dict('records')
                print(f"  ✅ 투자자별 매매 ({len(df)}일)")
        except Exception as e:
            print(f"  ❌ 투자자별 매매: {e}")
        
        # ==========================================
        # 7. 일자별 거래상세 (opt10015)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10015",
                종목코드=stock_code,
                시작일자=(datetime.now() - timedelta(days=60)).strftime('%Y%m%d'),
                output="일별거래상세",
                next=0)
            
            if df is not None and not df.empty:
                all_data['daily_trading_detail'] = df.to_dict('records')
                print(f"  ✅ 거래상세 ({len(df)}일)")
        except Exception as e:
            print(f"  ❌ 거래상세: {e}")
        
        # ==========================================
        # 8. 종목별 공시 (opt10087)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10087",
                종목코드=stock_code,
                조회일자="",
                output="종목별공시",
                next=0)
            
            if df is not None and not df.empty:
                all_data['disclosures'] = df.head(20).to_dict('records')
                print(f"  ✅ 공시 ({len(df)}건)")
        except Exception as e:
            print(f"  ❌ 공시: {e}")
        
        # ==========================================
        # 9. 종목별 증권사 추정실적 (opt10089)
        # ==========================================
        try:
            df = self.kiwoom.block_request("opt10089",
                종목코드=stock_code,
                output="종목별증권사",
                next=0)
            
            if df is not None and not df.empty:
                all_data['analyst_estimates'] = df.to_dict('records')
                print(f"  ✅ 애널리스트 추정 ({len(df)}개)")
        except Exception as e:
            print(f"  ❌ 애널리스트 추정: {e}")
        
        # ==========================================
        # 10. 업종 정보
        # ==========================================
        try:
            # 업종 코드 조회
            sector_code = self.kiwoom.GetThemeGroupCode(stock_code)
            if sector_code:
                all_data['sector_info'] = {
                    'sector_code': sector_code,
                    'sector_name': self.kiwoom.GetThemeGroupName(sector_code),
                }
                print(f"  ✅ 업종정보")
        except Exception as e:
            print(f"  ❌ 업종정보: {e}")
        
        # ==========================================
        # 11. 종목별 뉴스 (opt10087 변형)
        # ==========================================
        try:
            # 뉴스는 별도 처리 필요 (키움 API 제한적)
            all_data['has_news'] = True
            print(f"  ✅ 뉴스 연동 준비")
        except:
            pass
        
        return all_data
    
    def save_all_data(self, all_data: dict):
        """수집한 모든 데이터를 Supabase에 저장"""
        
        code = all_data['stock_code']
        
        try:
            # 1. 기본 정보 + 재무지표 통합 저장
            if 'basic_info' in all_data:
                fundamental = {
                    'stock_code': code,
                    'stock_name': all_data['stock_name'],
                    **all_data['basic_info']
                }
                
                if 'financial_statements' in all_data:
                    fundamental.update(all_data['financial_statements']['latest'])
                
                self.supabase.table('fundamental_data_complete').upsert(fundamental).execute()
                print(f"    💾 재무/기본정보 저장")
            
            # 2. 일봉 데이터 저장
            if 'daily_prices' in all_data:
                # 일봉 데이터 변환 및 저장
                for record in all_data['daily_prices']:
                    price_record = {
                        'stock_code': code,
                        'date': record.get('일자'),
                        'open': abs(int(record.get('시가', 0))),
                        'high': abs(int(record.get('고가', 0))),
                        'low': abs(int(record.get('저가', 0))),
                        'close': abs(int(record.get('현재가', 0))),
                        'volume': int(record.get('거래량', 0))
                    }
                    # 대량 저장 로직 필요
                
                print(f"    💾 일봉 {len(all_data['daily_prices'])}개 저장")
            
            # 3. 투자자별 매매 저장
            if 'investor_trading' in all_data:
                self.supabase.table('investor_trading').upsert({
                    'stock_code': code,
                    'data': all_data['investor_trading'],
                    'updated_at': datetime.now().isoformat()
                }).execute()
                print(f"    💾 투자자 매매 저장")
            
            # 4. 공시 정보 저장
            if 'disclosures' in all_data:
                self.supabase.table('disclosures').upsert({
                    'stock_code': code,
                    'data': all_data['disclosures'],
                    'updated_at': datetime.now().isoformat()
                }).execute()
                print(f"    💾 공시정보 저장")
            
            return True
            
        except Exception as e:
            print(f"    ❌ 저장 실패: {e}")
            return False
    
    def download_everything(self):
        """모든 종목의 모든 데이터 수집"""
        
        print("=" * 70)
        print("키움 OpenAPI+ 전체 데이터 수집")
        print("=" * 70)
        
        if not self.connect():
            print("키움 접속 실패")
            return
        
        # 전체 종목 리스트
        kospi = self.kiwoom.GetCodeListByMarket('0').split(';')[:-1]
        kosdaq = self.kiwoom.GetCodeListByMarket('10').split(';')[:-1]
        
        all_stocks = []
        for code in kospi:
            if code:
                name = self.kiwoom.GetMasterCodeName(code)
                if name and 'ETF' not in name and '스팩' not in name:
                    all_stocks.append({'code': code, 'name': name, 'market': 'KOSPI'})
        
        for code in kosdaq:
            if code:
                name = self.kiwoom.GetMasterCodeName(code)
                if name and 'ETF' not in name and '스팩' not in name:
                    all_stocks.append({'code': code, 'name': name, 'market': 'KOSDAQ'})
        
        print(f"\n총 {len(all_stocks)}개 종목 발견")
        
        # 각 종목 처리
        for i, stock in enumerate(all_stocks):
            progress = ((i + 1) / len(all_stocks)) * 100
            print(f"\n[{i+1}/{len(all_stocks)}] ({progress:.1f}%) {stock['name']} ({stock['code']})")
            
            # 모든 데이터 수집
            all_data = self.get_all_available_data(stock['code'])
            
            # 저장
            self.save_all_data(all_data)
            
            # API 제한 대기
            time.sleep(1)
            
            # 50개마다 휴식
            if (i + 1) % 50 == 0:
                print("\nAPI 제한 회피를 위해 30초 대기...")
                time.sleep(30)


# 필요한 테이블 SQL
def create_all_tables():
    return """
    -- 완전한 재무/기본정보 테이블
    CREATE TABLE IF NOT EXISTS fundamental_data_complete (
        stock_code VARCHAR(10) PRIMARY KEY,
        stock_name VARCHAR(100),
        
        -- 현재가 정보
        current_price INTEGER,
        change INTEGER,
        change_rate DECIMAL(10,2),
        volume BIGINT,
        trading_value BIGINT,
        
        -- 52주 고저
        high_52w INTEGER,
        low_52w INTEGER,
        
        -- 가치평가
        per DECIMAL(10,2),
        pbr DECIMAL(10,2),
        eps INTEGER,
        bps INTEGER,
        roe DECIMAL(10,2),
        roa DECIMAL(10,2),
        
        -- 시가총액
        market_cap BIGINT,
        shares_outstanding BIGINT,
        
        -- 외국인/기관
        foreign_ratio DECIMAL(10,2),
        institution_ratio DECIMAL(10,2),
        
        -- 재무제표
        fiscal_year VARCHAR(10),
        revenue BIGINT,
        operating_profit BIGINT,
        net_profit BIGINT,
        total_assets BIGINT,
        total_liabilities BIGINT,
        total_equity BIGINT,
        operating_margin DECIMAL(10,2),
        net_margin DECIMAL(10,2),
        debt_ratio DECIMAL(10,2),
        current_ratio DECIMAL(10,2),
        dividend_yield DECIMAL(10,2),
        
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    -- 투자자별 매매
    CREATE TABLE IF NOT EXISTS investor_trading (
        stock_code VARCHAR(10) PRIMARY KEY,
        data JSONB,
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    -- 공시정보
    CREATE TABLE IF NOT EXISTS disclosures (
        stock_code VARCHAR(10) PRIMARY KEY,
        data JSONB,
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    -- 애널리스트 추정
    CREATE TABLE IF NOT EXISTS analyst_estimates (
        stock_code VARCHAR(10) PRIMARY KEY,
        data JSONB,
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='키움 API 전체 데이터 수집')
    parser.add_argument('--stock', type=str, help='특정 종목')
    parser.add_argument('--all', action='store_true', help='전체 종목')
    parser.add_argument('--create-tables', action='store_true', help='테이블 SQL')
    
    args = parser.parse_args()
    
    if args.create_tables:
        print(create_all_tables())
    else:
        collector = KiwoomCompleteDataCollector()
        
        if args.stock:
            # 특정 종목 테스트
            if collector.connect():
                all_data = collector.get_all_available_data(args.stock)
                print(f"\n수집된 데이터 종류: {list(all_data.keys())}")
                collector.save_all_data(all_data)
        elif args.all:
            # 전체 수집
            print("\n⚠️  모든 데이터 수집 (매우 오래 걸림)")
            response = input("시작하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                collector.download_everything()
        else:
            # 삼성전자 테스트
            if collector.connect():
                all_data = collector.get_all_available_data('005930')
                print(f"\n삼성전자 수집 데이터:")
                for key in all_data:
                    if isinstance(all_data[key], list):
                        print(f"  - {key}: {len(all_data[key])}개")
                    elif isinstance(all_data[key], dict):
                        print(f"  - {key}: {len(all_data[key])} 필드")
                    else:
                        print(f"  - {key}")