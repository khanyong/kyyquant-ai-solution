"""
백테스트 API 라우트
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
# import yfinance as yf  # Yahoo Finance 대신 키움증권 API 사용
from typing import Dict, Any, List
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.kiwoom_data_api import KiwoomDataAPI, get_backtest_data
from strategies.base_strategy import BaseStrategy
from strategies.momentum_strategy import MomentumStrategy
from core.strategy_manager import StrategyManager
from core.supabase_client import get_supabase_client

backtest_bp = Blueprint('backtest', __name__)
executor = ThreadPoolExecutor(max_workers=4)

class BacktestEngine:
    """백테스트 실행 엔진"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.running_backtests = {}
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = '1d') -> pd.DataFrame:
        """키움증권 API 또는 Supabase에서 과거 데이터 가져오기"""
        try:
            # 키움증권 API 초기화
            if not hasattr(self, 'kiwoom_api'):
                self.kiwoom_api = KiwoomDataAPI()
                
                # 키움 API 인증 (Supabase에서 키 가져오기)
                auth_result = self.supabase.table('strategies').select('config').limit(1).execute()
                if auth_result.data:
                    config = auth_result.data[0].get('config', {})
                    app_key = config.get('KIWOOM_APP_KEY', 'iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk')
                    app_secret = config.get('KIWOOM_APP_SECRET', '9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA')
                else:
                    # 기본값 사용
                    app_key = 'iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk'
                    app_secret = '9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA'
                
                self.kiwoom_api.authenticate(app_key, app_secret)
            
            # 키움 API로 데이터 조회 (캐시 우선)
            data = self.kiwoom_api.get_historical_data(
                stock_code=symbol,
                start_date=start_date,
                end_date=end_date,
                use_cache=True  # Supabase 캐시 사용
            )
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            
            # 폴백: Supabase에서 직접 조회
            try:
                result = self.supabase.table('price_data').select('*')\
                    .eq('stock_code', symbol)\
                    .gte('date', start_date)\
                    .lte('date', end_date)\
                    .order('date', desc=False)\
                    .execute()
                
                if result.data:
                    df = pd.DataFrame(result.data)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                    return df
            except:
                pass
                
            return pd.DataFrame()
    
    def run_backtest(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """백테스트 실행"""
        backtest_id = str(uuid.uuid4())
        self.running_backtests[backtest_id] = {'status': 'running', 'progress': 0}
        
        try:
            # 전략 로드
            strategy_data = self.supabase.table('strategies').select('*').eq('id', config['strategy_id']).single().execute()
            if not strategy_data.data:
                raise ValueError(f"Strategy not found: {config['strategy_id']}")
            
            strategy_info = strategy_data.data
            
            # 전략 인스턴스 생성 (config 컬럼 사용)
            strategy_params = strategy_info.get('config') or strategy_info.get('parameters') or {}
            strategy_type = strategy_params.get('strategy_type') or strategy_info.get('type') or 'custom'
            
            if strategy_type == 'momentum':
                strategy = MomentumStrategy(
                    name=strategy_info['name'],
                    parameters=strategy_params
                )
            elif strategy_type == 'sma':
                from backend.strategies.simple_moving_average import SimpleMovingAverageStrategy
                strategy = SimpleMovingAverageStrategy(
                    name=strategy_info['name'],
                    parameters=strategy_params
                )
            elif strategy_type == 'rsi':
                from backend.strategies.rsi_strategy import RSIStrategy
                strategy = RSIStrategy(
                    name=strategy_info['name'],
                    parameters=strategy_params
                )
            elif strategy_type == 'bollinger':
                # 볼린저 밴드 전략은 베이스 전략으로 대체
                strategy = MomentumStrategy(
                    name=strategy_info['name'],
                    parameters=strategy_params
                )
            else:
                # 기본 전략 사용
                strategy = MomentumStrategy(
                    name=strategy_info['name'],
                    parameters=strategy_params
                )
            
            # 종목 코드 가져오기
            stock_codes = config.get('stock_codes', [])
            if not stock_codes:
                # 종목 코드가 없으면 주요 종목 사용
                stock_codes = ['005930', '000660', '035720', '005380', '051910']  # 삼성전자, SK하이닉스, 카카오, 현대차, LG화학
            
            # 백테스트 결과 초기화
            all_trades = []
            daily_returns = []
            portfolio_value = config['initial_capital']
            cash = config['initial_capital']
            positions = {}
            
            # 각 종목에 대해 백테스트 실행
            for i, stock_code in enumerate(stock_codes):
                progress = int((i / len(stock_codes)) * 100)
                self.running_backtests[backtest_id]['progress'] = progress
                
                # 과거 데이터 가져오기
                data = self.get_historical_data(
                    stock_code,
                    config['start_date'],
                    config['end_date'],
                    config.get('data_interval', '1d')
                )
                
                if data.empty:
                    continue
                
                # 전략 백테스트 실행
                result = strategy.backtest(data, cash / len(stock_codes))
                
                # 거래 내역 수집
                for trade in result.get('trades_history', []):
                    trade['stock_code'] = stock_code
                    all_trades.append(trade)
            
            # 백테스트 결과 계산
            total_trades = len(all_trades)
            profitable_trades = sum(1 for i in range(0, len(all_trades)-1, 2) 
                                   if i+1 < len(all_trades) and all_trades[i+1]['price'] > all_trades[i]['price'])
            
            win_rate = profitable_trades / (total_trades // 2) if total_trades >= 2 else 0
            
            # 최종 포트폴리오 가치 계산
            final_value = cash
            for stock_code, position in positions.items():
                last_data = self.get_historical_data(
                    stock_code,
                    config['end_date'],
                    config['end_date'],
                    '1d'
                )
                if not last_data.empty:
                    final_value += position['quantity'] * last_data['close'].iloc[-1]
            
            total_return = (final_value - config['initial_capital']) / config['initial_capital']
            
            # 연간 수익률 계산
            days = (datetime.strptime(config['end_date'], '%Y-%m-%d') - 
                   datetime.strptime(config['start_date'], '%Y-%m-%d')).days
            annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
            
            # 백테스트 결과 저장
            backtest_result = {
                'id': backtest_id,
                'strategy_id': config['strategy_id'],
                'strategy_name': strategy_info['name'],
                'user_id': config.get('user_id', 'f912da32-897f-4dbb-9242-3a438e9733a8'),
                'start_date': config['start_date'],
                'end_date': config['end_date'],
                'initial_capital': config['initial_capital'],
                'final_capital': final_value,
                'total_return': total_return,
                'annual_return': annual_return,
                'max_drawdown': 0.15,  # 임시값
                'volatility': 0.2,  # 임시값
                'sharpe_ratio': annual_return / 0.2 if annual_return > 0 else 0,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'profitable_trades': profitable_trades,
                'results_data': {
                    'stock_codes': stock_codes,
                    'config': config
                }
            }
            
            # Supabase에 저장
            self.supabase.table('backtest_results').insert(backtest_result).execute()
            
            # 거래 내역 저장
            if all_trades:
                trades_to_save = []
                for trade in all_trades:
                    trades_to_save.append({
                        'backtest_id': backtest_id,
                        'trade_date': trade.get('date', datetime.now()).isoformat() if isinstance(trade.get('date'), datetime) else str(trade.get('date')),
                        'stock_code': trade['stock_code'],
                        'stock_name': trade['stock_code'],  # 임시
                        'action': trade['type'].upper(),
                        'price': trade['price'],
                        'quantity': trade['quantity'],
                        'amount': trade['price'] * trade['quantity']
                    })
                
                self.supabase.table('backtest_trades').insert(trades_to_save).execute()
            
            self.running_backtests[backtest_id] = {'status': 'completed', 'progress': 100}
            
            return {
                'success': True,
                'backtest_id': backtest_id,
                'result': backtest_result
            }
            
        except Exception as e:
            self.running_backtests[backtest_id] = {
                'status': 'failed',
                'progress': 0,
                'error': str(e)
            }
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_backtest_status(self, backtest_id: str) -> Dict[str, Any]:
        """백테스트 상태 조회"""
        return self.running_backtests.get(backtest_id, {'status': 'not_found'})
    
    def stop_backtest(self, backtest_id: str) -> bool:
        """백테스트 중단"""
        if backtest_id in self.running_backtests:
            self.running_backtests[backtest_id] = {
                'status': 'stopped',
                'progress': self.running_backtests[backtest_id].get('progress', 0)
            }
            return True
        return False

# 백테스트 엔진 인스턴스
backtest_engine = BacktestEngine()

@backtest_bp.route('/run', methods=['POST'])
def run_backtest():
    """백테스트 실행"""
    try:
        config = request.json
        
        # 필수 파라미터 검증
        required_fields = ['strategy_id', 'start_date', 'end_date', 'initial_capital']
        for field in required_fields:
            if field not in config:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 비동기로 백테스트 실행
        future = executor.submit(backtest_engine.run_backtest, config)
        result = future.result(timeout=300)  # 5분 타임아웃
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backtest_bp.route('/status/<backtest_id>', methods=['GET'])
def get_backtest_status(backtest_id):
    """백테스트 상태 조회"""
    try:
        status = backtest_engine.get_backtest_status(backtest_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backtest_bp.route('/stop/<backtest_id>', methods=['POST'])
def stop_backtest(backtest_id):
    """백테스트 중단"""
    try:
        success = backtest_engine.stop_backtest(backtest_id)
        if success:
            return jsonify({'message': 'Backtest stopped successfully'}), 200
        else:
            return jsonify({'error': 'Backtest not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backtest_bp.route('/results/<backtest_id>', methods=['GET'])
def get_backtest_results(backtest_id):
    """백테스트 결과 조회"""
    try:
        supabase = get_supabase_client()
        
        # 백테스트 결과 조회
        result = supabase.table('backtest_results').select('*').eq('id', backtest_id).single().execute()
        if not result.data:
            return jsonify({'error': 'Backtest result not found'}), 404
        
        # 거래 내역 조회
        trades = supabase.table('backtest_trades').select('*').eq('backtest_id', backtest_id).execute()
        
        return jsonify({
            'result': result.data,
            'trades': trades.data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backtest_bp.route('/compare', methods=['POST'])
def compare_backtests():
    """여러 백테스트 결과 비교"""
    try:
        backtest_ids = request.json.get('backtest_ids', [])
        if not backtest_ids:
            return jsonify({'error': 'No backtest IDs provided'}), 400
        
        supabase = get_supabase_client()
        results = supabase.table('backtest_results').select('*').in_('id', backtest_ids).execute()
        
        return jsonify({'results': results.data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500