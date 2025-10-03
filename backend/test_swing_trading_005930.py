"""
스윙 트레이딩 전략 005930 백테스트 디버깅
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from supabase import create_client
from backtest.engine import BacktestEngine

async def test_swing_trading():
    # Supabase 클라이언트
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    # 스윙 트레이딩 전략 config
    strategy_config = {
        "indicators": [
            {"name": "sma", "params": {"period": 20}},
            {"name": "sma", "params": {"period": 60}},
            {"name": "rsi", "params": {"period": 14}},
            {"name": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
        ],
        "buyConditions": [
            {"left": "sma_20", "right": "sma_60", "operator": ">"},
            {"left": "rsi", "right": 60, "operator": "<"},
            {"left": "macd_line", "right": 0, "operator": ">"}
        ],
        "sellConditions": [
            {"left": "sma_20", "right": "sma_60", "operator": "<"},
            {"left": "rsi", "right": 70, "operator": ">"}
        ],
        "riskManagement": {
            "stopLoss": -5,
            "takeProfit": 10,
            "maxPositions": 5,
            "positionSize": 20,
            "trailingStop": False,
            "trailingStopPercent": 0
        }
    }

    # 백테스트 엔진
    engine = BacktestEngine(supabase_client=supabase)

    # 기간 설정 (1년)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print("=" * 80)
    print("스윙 트레이딩 전략 백테스트 - 005930 (삼성전자)")
    print("=" * 80)
    print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print()

    try:
        # 백테스트 실행
        result = await engine.run_backtest(
            strategy_config=strategy_config,
            stock_codes=['005930'],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            initial_capital=10000000
        )

        print("백테스트 완료!")
        print()
        print(f"총 수익률: {result.get('total_return', 0):.2f}%")
        print(f"거래 횟수: {result.get('trade_count', 0)}")
        print(f"승률: {result.get('win_rate', 0):.2f}%")
        print(f"최대 낙폭: {result.get('max_drawdown', 0):.2f}%")
        print()

        # 거래 내역 확인
        trades = result.get('trades', [])
        if trades:
            print(f"거래 내역 (최근 10건):")
            for trade in trades[:10]:
                print(f"  {trade.get('date')} | {trade.get('action')} | "
                      f"가격: {trade.get('price'):,.0f} | "
                      f"수량: {trade.get('quantity')} | "
                      f"수익률: {trade.get('return', 0):.2f}%")
        else:
            print("❌ 거래 내역이 없습니다!")
            print()
            print("디버깅 정보:")
            print(f"  - DataFrame 길이: {result.get('debug_info', {}).get('df_length', 'N/A')}")
            print(f"  - 컬럼: {result.get('debug_info', {}).get('columns', 'N/A')}")
            print(f"  - 매수 신호 발생 횟수: {result.get('debug_info', {}).get('buy_signals', 'N/A')}")
            print(f"  - 매도 신호 발생 횟수: {result.get('debug_info', {}).get('sell_signals', 'N/A')}")

    except Exception as e:
        print(f"❌ 백테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_swing_trading())
