"""
Supabase 데이터베이스 관리 모듈
PostgreSQL 기반으로 SQLite와 호환되는 인터페이스 제공
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseDatabase:
    """Supabase 데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.init_database()
    
    def init_database(self):
        """데이터베이스 테이블 초기화 (Supabase Dashboard에서 실행할 SQL)"""
        # 이 SQL은 Supabase Dashboard의 SQL Editor에서 실행해야 합니다
        init_sql = """
        -- 주문 내역 테이블
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_id TEXT UNIQUE,
            stock_code TEXT NOT NULL,
            stock_name TEXT,
            order_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            order_method TEXT,
            status TEXT DEFAULT 'pending',
            executed_price DECIMAL(10, 2),
            executed_quantity INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            executed_at TIMESTAMPTZ,
            strategy TEXT,
            notes TEXT,
            user_id UUID REFERENCES auth.users(id)
        );
        
        -- 포트폴리오 테이블
        CREATE TABLE IF NOT EXISTS portfolio (
            id SERIAL PRIMARY KEY,
            stock_code TEXT NOT NULL,
            stock_name TEXT,
            quantity INTEGER NOT NULL,
            avg_price DECIMAL(10, 2) NOT NULL,
            current_price DECIMAL(10, 2),
            profit_loss DECIMAL(10, 2),
            profit_loss_rate DECIMAL(5, 2),
            last_updated TIMESTAMPTZ DEFAULT NOW(),
            user_id UUID REFERENCES auth.users(id),
            UNIQUE(stock_code, user_id)
        );
        
        -- 가격 데이터 테이블
        CREATE TABLE IF NOT EXISTS price_data (
            id SERIAL PRIMARY KEY,
            stock_code TEXT NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            open DECIMAL(10, 2),
            high DECIMAL(10, 2),
            low DECIMAL(10, 2),
            close DECIMAL(10, 2) NOT NULL,
            volume BIGINT,
            UNIQUE(stock_code, timestamp)
        );
        
        -- 거래 신호 테이블
        CREATE TABLE IF NOT EXISTS signals (
            id SERIAL PRIMARY KEY,
            stock_code TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            strategy TEXT NOT NULL,
            strength DECIMAL(3, 2),
            price DECIMAL(10, 2),
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            executed BOOLEAN DEFAULT FALSE,
            notes TEXT,
            user_id UUID REFERENCES auth.users(id)
        );
        
        -- 성과 분석 테이블
        CREATE TABLE IF NOT EXISTS performance (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            total_value DECIMAL(15, 2),
            daily_return DECIMAL(10, 4),
            cumulative_return DECIMAL(10, 4),
            win_rate DECIMAL(5, 2),
            trades_count INTEGER,
            profit_trades INTEGER,
            loss_trades INTEGER,
            max_drawdown DECIMAL(10, 4),
            sharpe_ratio DECIMAL(10, 4),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            user_id UUID REFERENCES auth.users(id),
            UNIQUE(date, user_id)
        );
        
        -- 시스템 로그 테이블
        CREATE TABLE IF NOT EXISTS system_logs (
            id SERIAL PRIMARY KEY,
            level TEXT NOT NULL,
            module TEXT,
            message TEXT NOT NULL,
            details JSONB,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            user_id UUID REFERENCES auth.users(id)
        );
        
        -- 인덱스 생성
        CREATE INDEX IF NOT EXISTS idx_orders_stock_code ON orders(stock_code);
        CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
        CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio(user_id);
        CREATE INDEX IF NOT EXISTS idx_price_data_stock_timestamp ON price_data(stock_code, timestamp);
        CREATE INDEX IF NOT EXISTS idx_signals_stock_code ON signals(stock_code);
        CREATE INDEX IF NOT EXISTS idx_performance_date_user ON performance(date, user_id);
        
        -- RLS (Row Level Security) 정책
        ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
        ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
        ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
        ALTER TABLE performance ENABLE ROW LEVEL SECURITY;
        ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;
        
        -- 사용자별 데이터 접근 정책
        CREATE POLICY "Users can view own orders" ON orders
            FOR ALL USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can view own portfolio" ON portfolio
            FOR ALL USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can view own signals" ON signals
            FOR ALL USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can view own performance" ON performance
            FOR ALL USING (auth.uid() = user_id);
        
        CREATE POLICY "Users can view own logs" ON system_logs
            FOR ALL USING (auth.uid() = user_id);
        
        -- 가격 데이터는 모든 사용자가 볼 수 있음
        CREATE POLICY "Anyone can view price data" ON price_data
            FOR SELECT USING (true);
        """
        print("Database tables initialized. Please run the SQL above in Supabase Dashboard.")
    
    def add_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """주문 기록 추가"""
        try:
            # user_id 추가 (인증된 사용자의 경우)
            if hasattr(self.client.auth, 'user') and self.client.auth.user:
                order_data['user_id'] = self.client.auth.user.id
            
            response = self.client.table('orders').insert(order_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding order: {e}")
            return None
    
    def update_order_status(self, order_id: str, status: str, 
                           executed_price: float = None, 
                           executed_quantity: int = None):
        """주문 상태 업데이트"""
        try:
            update_data = {'status': status}
            if executed_price and executed_quantity:
                update_data.update({
                    'executed_price': executed_price,
                    'executed_quantity': executed_quantity,
                    'executed_at': datetime.now().isoformat()
                })
            
            response = self.client.table('orders').update(update_data).eq('order_id', order_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating order status: {e}")
            return None
    
    def update_portfolio(self, stock_code: str, quantity: int, 
                        avg_price: float, current_price: float = None):
        """포트폴리오 업데이트"""
        try:
            user_id = None
            if hasattr(self.client.auth, 'user') and self.client.auth.user:
                user_id = self.client.auth.user.id
            
            # 기존 포지션 확인
            response = self.client.table('portfolio').select('*').eq('stock_code', stock_code)
            if user_id:
                response = response.eq('user_id', user_id)
            existing = response.execute()
            
            if existing.data:
                # 기존 포지션 업데이트
                old_data = existing.data[0]
                old_qty = old_data['quantity']
                old_avg = float(old_data['avg_price'])
                new_qty = old_qty + quantity
                
                if new_qty <= 0:
                    # 포지션 청산
                    self.client.table('portfolio').delete().eq('id', old_data['id']).execute()
                else:
                    # 평균가 재계산
                    if quantity > 0:  # 매수
                        new_avg = (old_qty * old_avg + quantity * avg_price) / new_qty
                    else:  # 매도
                        new_avg = old_avg
                    
                    profit_loss = (current_price - new_avg) * new_qty if current_price else 0
                    profit_loss_rate = (profit_loss / (new_avg * new_qty)) * 100 if new_qty > 0 else 0
                    
                    update_data = {
                        'quantity': new_qty,
                        'avg_price': new_avg,
                        'current_price': current_price,
                        'profit_loss': profit_loss,
                        'profit_loss_rate': profit_loss_rate,
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    self.client.table('portfolio').update(update_data).eq('id', old_data['id']).execute()
            else:
                # 새 포지션 추가
                portfolio_data = {
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'current_price': current_price
                }
                if user_id:
                    portfolio_data['user_id'] = user_id
                
                self.client.table('portfolio').insert(portfolio_data).execute()
        except Exception as e:
            print(f"Error updating portfolio: {e}")
    
    def add_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """거래 신호 추가"""
        try:
            if hasattr(self.client.auth, 'user') and self.client.auth.user:
                signal_data['user_id'] = self.client.auth.user.id
            
            response = self.client.table('signals').insert(signal_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding signal: {e}")
            return None
    
    def add_price_data(self, stock_code: str, price_data: Dict[str, Any]):
        """가격 데이터 추가 (upsert)"""
        try:
            price_data['stock_code'] = stock_code
            response = self.client.table('price_data').upsert(
                price_data,
                on_conflict='stock_code,timestamp'
            ).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding price data: {e}")
            return None
    
    def get_price_history(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """가격 이력 조회"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            response = self.client.table('price_data').select('*').eq(
                'stock_code', stock_code
            ).gte('timestamp', start_date).order('timestamp').execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting price history: {e}")
            return pd.DataFrame()
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """현재 포트폴리오 조회"""
        try:
            query = self.client.table('portfolio').select('*').gt('quantity', 0)
            
            if hasattr(self.client.auth, 'user') and self.client.auth.user:
                query = query.eq('user_id', self.client.auth.user.id)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return []
    
    def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 주문 내역 조회"""
        try:
            query = self.client.table('orders').select('*').order(
                'created_at', desc=True
            ).limit(limit)
            
            if hasattr(self.client.auth, 'user') and self.client.auth.user:
                query = query.eq('user_id', self.client.auth.user.id)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting recent orders: {e}")
            return []
    
    def calculate_performance(self, date: str = None):
        """성과 계산 및 저장"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            user_id = None
            if hasattr(self.client.auth, 'user') and self.client.auth.user:
                user_id = self.client.auth.user.id
            
            # 오늘의 거래 통계
            query = self.client.table('orders').select('*').eq(
                'status', 'executed'
            ).gte('executed_at', f"{date}T00:00:00").lt('executed_at', f"{date}T23:59:59")
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            orders_response = query.execute()
            orders = orders_response.data if orders_response.data else []
            
            trades_count = len(orders)
            profit_trades = sum(1 for o in orders if float(o.get('executed_price', 0)) * o.get('executed_quantity', 0) > float(o.get('price', 0)) * o.get('quantity', 0))
            loss_trades = trades_count - profit_trades
            win_rate = (profit_trades / trades_count * 100) if trades_count > 0 else 0
            
            # 포트폴리오 총 가치
            portfolio = self.get_portfolio()
            total_value = sum(p['quantity'] * float(p.get('current_price', 0)) for p in portfolio)
            
            # 성과 저장
            performance_data = {
                'date': date,
                'total_value': total_value,
                'win_rate': win_rate,
                'trades_count': trades_count,
                'profit_trades': profit_trades,
                'loss_trades': loss_trades
            }
            
            if user_id:
                performance_data['user_id'] = user_id
            
            self.client.table('performance').upsert(
                performance_data,
                on_conflict='date,user_id' if user_id else 'date'
            ).execute()
        except Exception as e:
            print(f"Error calculating performance: {e}")
    
    def add_log(self, level: str, module: str, message: str, details: Dict = None):
        """시스템 로그 추가"""
        try:
            log_data = {
                'level': level,
                'module': module,
                'message': message,
                'details': details or {}
            }
            
            if hasattr(self.client.auth, 'user') and self.client.auth.user:
                log_data['user_id'] = self.client.auth.user.id
            
            self.client.table('system_logs').insert(log_data).execute()
        except Exception as e:
            print(f"Error adding log: {e}")
    
    def bulk_insert_price_data(self, price_data_list: List[Dict[str, Any]]):
        """대량 가격 데이터 삽입"""
        try:
            response = self.client.table('price_data').upsert(
                price_data_list,
                on_conflict='stock_code,timestamp'
            ).execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"Error bulk inserting price data: {e}")
            return 0