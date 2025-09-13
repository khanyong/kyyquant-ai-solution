"""
실제 시장 데이터로 백테스트 테스트
"""
import asyncio
import sys
import json
from datetime import datetime, timedelta
sys.path.append('.')
from api.backtest_api import BacktestEngine
from api.kiwoom_data_api import KiwoomDataAPI

async def test_real_data_backtest():
    """실제 시장 데이터로 백테스트 테스트"""
    
    print("=" * 50)
    print("실제 시장 데이터 백테스트 테스트")
    print("=" * 50)
    
    # 1. 키움 API로 실제 데이터 다운로드
    kiwoom_api = KiwoomDataAPI()
    
    # 테스트용 종목 코드 (삼성전자, SK하이닉스)
    stock_codes = ['005930', '000660']
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
    end_date = datetime.now().strftime('%Y%m%d')
    
    print(f"\n데이터 다운로드 중...")
    print(f"종목: {stock_codes}")
    print(f"기간: {start_date} ~ {end_date}")
    
    price_data = {}
    for stock_code in stock_codes:
        try:
            print(f"\n{stock_code} 데이터 다운로드 중...")
            data = await kiwoom_api.get_stock_price_data(
                stock_code, 
                start_date, 
                end_date,
                data_type='D'  # 일봉 데이터
            )
            
            if data is not None and not data.empty:
                price_data[stock_code] = data
                print(f"  - 다운로드 완료: {len(data)}개 데이터")
                print(f"  - 가격 범위: {data['close'].min():.0f} ~ {data['close'].max():.0f}")
            else:
                print(f"  - 데이터 없음")
        except Exception as e:
            print(f"  - 다운로드 실패: {e}")
    
    if not price_data:
        print("\n데이터 다운로드 실패 - 모의 데이터 사용")
        # 모의 데이터 생성
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(42)
        
        for stock_code in stock_codes:
            # 현실적인 주가 데이터 생성
            base_price = 70000 if stock_code == '005930' else 120000
            returns = np.random.normal(0.001, 0.02, len(dates))
            prices = base_price * np.exp(np.cumsum(returns))
            
            price_data[stock_code] = pd.DataFrame({
                'open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
                'high': prices * (1 + np.abs(np.random.uniform(0, 0.02, len(dates)))),
                'low': prices * (1 - np.abs(np.random.uniform(0, 0.02, len(dates)))),
                'close': prices,
                'volume': np.random.uniform(10000000, 30000000, len(dates)),
                'trading_value': prices * np.random.uniform(10000000, 30000000, len(dates))
            }, index=dates)
            
            print(f"\n{stock_code} 모의 데이터 생성 완료")
            print(f"  - 데이터 개수: {len(price_data[stock_code])}개")
            print(f"  - 가격 범위: {prices.min():.0f} ~ {prices.max():.0f}")
    
    # 2. 백테스트 전략 설정
    strategy = {
        'name': 'RSI + MACD Strategy',
        'config': {
            'useStageBasedStrategy': False,
            'buyConditions': [
                {
                    'indicator': 'rsi',
                    'operator': '<',
                    'value': 30
                }
            ],
            'sellConditions': [
                {
                    'indicator': 'rsi',
                    'operator': '>',
                    'value': 70
                }
            ]
        }
    }
    
    print("\n" + "=" * 50)
    print("백테스트 전략")
    print("=" * 50)
    print(f"매수 조건: RSI < 30")
    print(f"매도 조건: RSI > 70")
    
    # 3. 백테스트 실행
    engine = BacktestEngine()
    
    print("\n" + "=" * 50)
    print("백테스트 실행")
    print("=" * 50)
    
    result = await engine.run_backtest(
        strategy=strategy,
        price_data=price_data,
        initial_capital=100000000,  # 1억원
        commission=0.00015,
        slippage=0.001,
        data_interval='1d'
    )
    
    # 4. 결과 출력
    print("\n" + "=" * 50)
    print("백테스트 결과")
    print("=" * 50)
    print(f"초기 자본: 100,000,000원")
    print(f"최종 자산: {result.get('final_value', 0):,.0f}원")
    print(f"총 수익률: {result['total_return']:.2f}%")
    print(f"총 거래 횟수: {result['total_trades']}")
    print(f"승률: {result['win_rate']:.2f}%")
    print(f"최대 손실률(MDD): {result.get('max_drawdown', 0):.2f}%")
    print(f"샤프 비율: {result.get('sharpe_ratio', 0):.2f}")
    
    if result['trades']:
        print(f"\n최근 거래 내역 (최대 10개):")
        for i, trade in enumerate(result['trades'][:10], 1):
            stock = trade.get('stock', 'N/A')
            print(f"  {i}. {trade['date']}: {trade['action']} {stock} @ {trade['price']:,.0f}원")
    else:
        print("\n거래가 발생하지 않았습니다.")
    
    # 5. 개별 종목 성과
    if 'stock_returns' in result:
        print(f"\n종목별 수익률:")
        for stock, ret in result['stock_returns'].items():
            print(f"  {stock}: {ret:.2f}%")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_real_data_backtest())
    print("\n테스트 완료!")