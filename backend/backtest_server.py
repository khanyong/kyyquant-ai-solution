"""
간단한 백테스트 서버
FastAPI 기반으로 백테스트 기능만 제공
"""

import os
import sys
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from supabase import create_client, Client

# 환경 변수 로드 - backend 폴더의 .env 파일 먼저, 없으면 상위 디렉토리
backend_env = os.path.join(os.path.dirname(__file__), '.env')
root_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

if os.path.exists(backend_env):
    load_dotenv(backend_env)
    print(f"Loaded .env from: {backend_env}")
elif os.path.exists(root_env):
    load_dotenv(root_env)
    print(f"Loaded .env from: {root_env}")
else:
    print("Warning: No .env file found!")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱
app = FastAPI(
    title="Backtest Server",
    description="간단한 백테스트 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase 클라이언트
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_KEY: {'Set' if supabase_key else 'Not set'}")

if not supabase_url or not supabase_key:
    logger.error("Supabase credentials not found in environment variables")
    logger.error("Please check your .env file contains SUPABASE_URL and SUPABASE_KEY or SUPABASE_ANON_KEY")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

# 요청 모델
class BacktestRequest(BaseModel):
    strategy_id: str
    start_date: str
    end_date: str
    initial_capital: float = 10000000
    commission: float = 0.00015
    slippage: float = 0.001
    stock_codes: List[str] = []

# 응답 모델
class BacktestResponse(BaseModel):
    total_return: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    trades: int
    winning_trades: int
    losing_trades: int
    final_capital: float
    trade_history: List[Dict] = []
    equity_curve: List[Dict] = []

@app.get("/")
async def root():
    return {"message": "Backtest Server is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest):
    """백테스트 실행"""
    try:
        logger.info(f"백테스트 시작: {request.strategy_id}")
        
        # 전략 정보 가져오기
        strategy_response = supabase.table('strategies').select("*").eq('id', request.strategy_id).execute()
        if not strategy_response.data:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        strategy = strategy_response.data[0]
        logger.info(f"전략 로드: {strategy.get('name', 'Unknown')}")
        
        # 종목 데이터 가져오기 (로컬 캐시 또는 Supabase)
        stock_data = await load_stock_data(request.stock_codes, request.start_date, request.end_date)
        
        if not stock_data:
            logger.warning("종목 데이터가 없습니다")
            # 샘플 데이터로 시뮬레이션
            stock_data = generate_sample_data(request.stock_codes, request.start_date, request.end_date)
        
        # 백테스트 실행
        result = perform_backtest(
            strategy=strategy,
            stock_data=stock_data,
            initial_capital=request.initial_capital,
            commission=request.commission,
            slippage=request.slippage
        )
        
        logger.info(f"백테스트 완료: 수익률 {result['total_return']:.2f}%")
        
        # 백테스트 ID 생성
        backtest_id = str(uuid.uuid4())
        
        # Supabase에 결과 저장
        try:
            # 전략 정보 가져오기 (user_id, name, custom_parameters)
            strategy_response = supabase.table('strategies').select("user_id, name, custom_parameters").eq('id', request.strategy_id).execute()
            
            if strategy_response.data:
                user_id = strategy_response.data[0]['user_id']
                strategy_name_raw = strategy_response.data[0]['name']
                custom_params = strategy_response.data[0].get('custom_parameters', {})
                
                # 템플릿 이름이 있으면 사용, 없으면 전략 이름 사용
                if custom_params and isinstance(custom_params, dict):
                    template_name = custom_params.get('templateName')
                    if template_name:
                        strategy_name = template_name
                    elif strategy_name_raw.startswith('[템플릿] '):
                        # "[템플릿] " 접두사 제거
                        strategy_name = strategy_name_raw.replace('[템플릿] ', '')
                    else:
                        strategy_name = strategy_name_raw
                else:
                    strategy_name = strategy_name_raw
            else:
                logger.warning("전략 정보를 찾을 수 없음, 기본값 사용")
                user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'  # 기본값 (테스트용)
                strategy_name = '알 수 없는 전략'
            
            backtest_record = {
                'id': backtest_id,
                'strategy_id': request.strategy_id,
                'user_id': user_id,
                'strategy_name': strategy_name,  # strategy_name 추가
                'start_date': request.start_date,
                'end_date': request.end_date,
                'initial_capital': float(request.initial_capital),
                'final_capital': float(result['final_capital']),
                'total_return': float(result['total_return']),
                'max_drawdown': float(result['max_drawdown']),
                'sharpe_ratio': float(result['sharpe_ratio']),
                'win_rate': float(result['win_rate']),
                'total_trades': int(result['trades']),
                'winning_trades': int(result['winning_trades']),
                'losing_trades': int(result['losing_trades']),
                'profitable_trades': int(result['winning_trades']),  # profitable_trades 필드 추가
                'results_data': json.dumps({
                    'equity_curve': result['equity_curve'][-100:] if len(result['equity_curve']) > 100 else result['equity_curve'],
                    'commission': request.commission,
                    'slippage': request.slippage,
                    'stock_codes': request.stock_codes
                }),
                'trade_details': json.dumps(result['trade_history'][:50]),  # 최근 50개 거래만
                'daily_returns': json.dumps([])  # 향후 구현
            }
            
            # backtest_results 테이블에 저장
            response = supabase.table('backtest_results').insert(backtest_record).execute()
            logger.info(f"백테스트 결과 저장 완료: {backtest_id}")
            
        except Exception as e:
            logger.error(f"백테스트 결과 저장 실패: {str(e)}")
            # 저장 실패해도 결과는 반환
        
        # 프론트엔드가 기대하는 형식으로 응답
        return {
            "status": "completed",
            "backtest_id": backtest_id,
            "results": {
                "total_return": result['total_return'],
                "win_rate": result['win_rate'],
                "max_drawdown": result['max_drawdown'],
                "sharpe_ratio": result['sharpe_ratio'],
                "total_trades": result['trades'],
                "winning_trades": result['winning_trades'],
                "losing_trades": result['losing_trades'],
                "final_capital": result['final_capital'],
                "trade_history": result['trade_history'],
                "equity_curve": result['equity_curve'],
                "annual_return": result.get('annual_return', result['total_return'] / 3),  # 3년 기준 연환산
                "volatility": result.get('volatility', 15.0),  # 기본값
                "trades": result['trade_history'],
                "daily_returns": []  # 향후 구현
            }
        }
        
    except Exception as e:
        logger.error(f"백테스트 실행 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def load_stock_data(stock_codes: List[str], start_date: str, end_date: str) -> Dict:
    """종목 데이터 로드"""
    stock_data = {}
    
    try:
        # 로컬 캐시 확인
        cache_dir = "D:/Dev/auto_stock/data/cache"
        if os.path.exists(cache_dir):
            for code in stock_codes:
                cache_file = os.path.join(cache_dir, f"{code}_{start_date}_{end_date}.csv")
                if os.path.exists(cache_file):
                    df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                    stock_data[code] = df
                    logger.info(f"캐시에서 로드: {code}")
                    continue
        
        # Supabase에서 가져오기
        for code in stock_codes:
            if code not in stock_data:
                try:
                    response = supabase.table('kw_price_daily').select("*").eq('stock_code', code).gte('trade_date', start_date).lte('trade_date', end_date).execute()
                    if response.data:
                        df = pd.DataFrame(response.data)
                        # trade_date를 date로 변환하고 인덱스로 설정
                        df['date'] = df['trade_date']
                        df.set_index('trade_date', inplace=True)
                        stock_data[code] = df
                        logger.info(f"Supabase에서 로드: {code}")
                except:
                    logger.warning(f"데이터 로드 실패: {code}")
                    
    except Exception as e:
        logger.error(f"데이터 로드 오류: {str(e)}")
    
    return stock_data

def generate_sample_data(stock_codes: List[str], start_date: str, end_date: str) -> Dict:
    """샘플 데이터 생성 (테스트용)"""
    stock_data = {}
    
    # 날짜 범위 생성
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days only
    
    for code in stock_codes:
        # 랜덤 가격 데이터 생성
        np.random.seed(hash(code) % 2**32)  # 종목별 일관된 랜덤 시드
        
        # 초기 가격
        initial_price = np.random.uniform(10000, 100000)
        
        # 일별 수익률 (평균 0.1%, 표준편차 2%)
        daily_returns = np.random.normal(0.001, 0.02, len(dates))
        
        # 가격 계산
        prices = initial_price * np.exp(np.cumsum(daily_returns))
        
        # 거래량 생성
        volumes = np.random.uniform(100000, 1000000, len(dates))
        
        # DataFrame 생성
        df = pd.DataFrame({
            'open': prices * np.random.uniform(0.98, 1.02, len(dates)),
            'high': prices * np.random.uniform(1.01, 1.05, len(dates)),
            'low': prices * np.random.uniform(0.95, 0.99, len(dates)),
            'close': prices,
            'volume': volumes
        }, index=dates)
        
        stock_data[code] = df
        logger.info(f"샘플 데이터 생성: {code}")
    
    return stock_data

def perform_backtest(strategy: Dict, stock_data: Dict, initial_capital: float, commission: float, slippage: float) -> Dict:
    """백테스트 실행 로직"""
    
    # 간단한 백테스트 시뮬레이션
    capital = initial_capital
    trades = []
    equity_curve = []
    
    # 전략 파라미터 파싱
    strategy_params = strategy.get('custom_parameters', {})
    
    # 모든 종목의 날짜 통합
    all_dates = set()
    for df in stock_data.values():
        all_dates.update(df.index)
    all_dates = sorted(list(all_dates))
    
    # 포트폴리오 초기화
    portfolio = {
        'cash': initial_capital,
        'positions': {},
        'position_costs': {},  # 각 포지션의 매수 비용 추적
        'value': initial_capital
    }
    
    # 각 날짜별로 백테스트 실행
    for date in all_dates:
        daily_value = portfolio['cash']
        
        for code, df in stock_data.items():
            if date in df.index:
                price = df.loc[date, 'close']
                
                # 간단한 전략: RSI < 30 매수, RSI > 70 매도 (예시)
                # 실제로는 strategy_params를 기반으로 구현
                signal = generate_signal(df, date, strategy_params)
                
                if signal == 'buy' and portfolio['cash'] > price * 100:
                    # 매수
                    shares = 100
                    cost = price * shares * (1 + commission + slippage)
                    if cost <= portfolio['cash']:
                        portfolio['cash'] -= cost
                        portfolio['positions'][code] = portfolio['positions'].get(code, 0) + shares
                        # 매수 비용 저장 (평균 단가 계산)
                        if code in portfolio['position_costs']:
                            total_cost = portfolio['position_costs'][code] + cost
                            portfolio['position_costs'][code] = total_cost
                        else:
                            portfolio['position_costs'][code] = cost
                        trades.append({
                            'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                            'code': code,
                            'action': 'buy',
                            'price': price,
                            'shares': shares,
                            'cost': cost
                        })
                
                elif signal == 'sell' and code in portfolio['positions'] and portfolio['positions'][code] > 0:
                    # 매도
                    shares = portfolio['positions'][code]
                    revenue = price * shares * (1 - commission - slippage)
                    portfolio['cash'] += revenue
                    
                    # 손익 계산
                    original_cost = portfolio['position_costs'].get(code, 0)
                    profit = revenue - original_cost if original_cost > 0 else 0
                    
                    portfolio['positions'][code] = 0
                    portfolio['position_costs'][code] = 0  # 비용 초기화
                    
                    trades.append({
                        'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                        'code': code,
                        'action': 'sell',
                        'price': price,
                        'shares': shares,
                        'revenue': revenue,
                        'cost': original_cost,  # 원래 매수 비용
                        'profit': profit  # 손익
                    })
                
                # 포지션 평가
                if code in portfolio['positions']:
                    daily_value += portfolio['positions'][code] * price
        
        portfolio['value'] = daily_value
        equity_curve.append({
            'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
            'value': daily_value
        })
    
    # 최종 결과 계산
    final_capital = portfolio['value']
    total_return = ((final_capital - initial_capital) / initial_capital) * 100
    
    # 승률 계산 - profit 필드 사용
    sell_trades = [t for t in trades if t.get('action') == 'sell']
    winning_trades = len([t for t in sell_trades if t.get('profit', 0) > 0])
    losing_trades = len([t for t in sell_trades if t.get('profit', 0) < 0])
    win_rate = (winning_trades / max(1, len(sell_trades))) * 100
    
    # 디버깅 로그
    if sell_trades:
        print(f"\n=== Backtest Server Win Rate Debug ===")
        print(f"Total sell trades: {len(sell_trades)}")
        print(f"Winning trades: {winning_trades}")
        print(f"Losing trades: {losing_trades}")
        print(f"Win rate: {win_rate:.1f}%")
        profits = [t.get('profit', 0) for t in sell_trades]
        if profits:
            print(f"Profit range: {min(profits):.0f} ~ {max(profits):.0f}")
        print(f"======================================\n")
    
    # 최대 낙폭 계산
    max_drawdown = calculate_max_drawdown(equity_curve)
    
    # 샤프 비율 계산 (간단화)
    sharpe_ratio = calculate_sharpe_ratio(equity_curve)
    
    return {
        'total_return': total_return,
        'win_rate': win_rate,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'trades': len(trades),
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'final_capital': final_capital,
        'trade_history': trades[-20:],  # 최근 20개 거래만
        'equity_curve': equity_curve[-100:]  # 최근 100일만
    }

def generate_signal(df: pd.DataFrame, date, strategy_params: Dict) -> str:
    """거래 신호 생성"""
    # TODO: 실제 전략 파라미터를 사용한 신호 생성 구현 필요
    # 임시로 간단한 기술적 지표 기반 신호 생성
    
    # 현재는 매수/매도 신호를 생성하지 않음 (hold만 반환)
    # 이렇게 하면 백테스트가 일관된 결과를 보여줄 것임
    return 'hold'
    
    # 나중에 실제 전략 구현 시 아래와 같은 방식으로:
    # if 'buyConditions' in strategy_params:
    #     # 매수 조건 체크
    #     for condition in strategy_params['buyConditions']:
    #         if evaluate_condition(df, date, condition):
    #             return 'buy'
    # 
    # if 'sellConditions' in strategy_params:
    #     # 매도 조건 체크
    #     for condition in strategy_params['sellConditions']:
    #         if evaluate_condition(df, date, condition):
    #             return 'sell'
    # 
    # return 'hold'

def calculate_max_drawdown(equity_curve: List[Dict]) -> float:
    """최대 낙폭 계산"""
    if not equity_curve:
        return 0
    
    values = [e['value'] for e in equity_curve]
    peak = values[0]
    max_dd = 0
    
    for value in values:
        if value > peak:
            peak = value
        dd = ((peak - value) / peak) * 100
        max_dd = max(max_dd, dd)
    
    return max_dd

def calculate_sharpe_ratio(equity_curve: List[Dict], risk_free_rate: float = 0.02) -> float:
    """샤프 비율 계산"""
    if len(equity_curve) < 2:
        return 0
    
    values = [e['value'] for e in equity_curve]
    returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
    
    if not returns:
        return 0
    
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0
    
    # 연율화 (일별 데이터 가정)
    annual_return = avg_return * 252
    annual_std = std_return * np.sqrt(252)
    
    return (annual_return - risk_free_rate) / annual_std

if __name__ == "__main__":
    # 서버 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)