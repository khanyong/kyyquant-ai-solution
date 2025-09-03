"""
데이터베이스 관리 모듈
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import json

class TradingDatabase:
    """거래 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "data/trading.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 주문 내역 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT,
                    order_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    order_method TEXT,
                    status TEXT DEFAULT 'pending',
                    executed_price REAL,
                    executed_quantity INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMP,
                    strategy TEXT,
                    notes TEXT
                )
            """)
            
            # 포트폴리오 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT UNIQUE,
                    stock_name TEXT,
                    quantity INTEGER NOT NULL,
                    avg_price REAL NOT NULL,
                    current_price REAL,
                    profit_loss REAL,
                    profit_loss_rate REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 가격 데이터 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL NOT NULL,
                    volume INTEGER,
                    UNIQUE(stock_code, timestamp)
                )
            """)
            
            # 거래 신호 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    strength REAL,
                    price REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed BOOLEAN DEFAULT FALSE,
                    notes TEXT
                )
            """)
            
            # 성과 분석 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    total_value REAL,
                    daily_return REAL,
                    cumulative_return REAL,
                    win_rate REAL,
                    trades_count INTEGER,
                    profit_trades INTEGER,
                    loss_trades INTEGER,
                    max_drawdown REAL,
                    sharpe_ratio REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 시스템 로그 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    module TEXT,
                    message TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_order(self, order_data: Dict[str, Any]) -> int:
        """주문 기록 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (
                    order_id, stock_code, stock_name, order_type, 
                    quantity, price, order_method, status, strategy, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_data.get('order_id'),
                order_data['stock_code'],
                order_data.get('stock_name'),
                order_data['order_type'],
                order_data['quantity'],
                order_data['price'],
                order_data.get('order_method', 'limit'),
                order_data.get('status', 'pending'),
                order_data.get('strategy'),
                order_data.get('notes')
            ))
            return cursor.lastrowid
    
    def update_order_status(self, order_id: str, status: str, 
                           executed_price: float = None, 
                           executed_quantity: int = None):
        """주문 상태 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if executed_price and executed_quantity:
                cursor.execute("""
                    UPDATE orders 
                    SET status = ?, executed_price = ?, 
                        executed_quantity = ?, executed_at = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                """, (status, executed_price, executed_quantity, order_id))
            else:
                cursor.execute("""
                    UPDATE orders SET status = ? WHERE order_id = ?
                """, (status, order_id))
            conn.commit()
    
    def update_portfolio(self, stock_code: str, quantity: int, 
                        avg_price: float, current_price: float = None):
        """포트폴리오 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 포지션 확인
            cursor.execute("SELECT quantity, avg_price FROM portfolio WHERE stock_code = ?", 
                          (stock_code,))
            existing = cursor.fetchone()
            
            if existing:
                # 기존 포지션 업데이트
                old_qty, old_avg = existing
                new_qty = old_qty + quantity
                
                if new_qty <= 0:
                    # 포지션 청산
                    cursor.execute("DELETE FROM portfolio WHERE stock_code = ?", 
                                 (stock_code,))
                else:
                    # 평균가 재계산
                    if quantity > 0:  # 매수
                        new_avg = (old_qty * old_avg + quantity * avg_price) / new_qty
                    else:  # 매도
                        new_avg = old_avg
                    
                    profit_loss = (current_price - new_avg) * new_qty if current_price else 0
                    profit_loss_rate = (profit_loss / (new_avg * new_qty)) * 100 if new_qty > 0 else 0
                    
                    cursor.execute("""
                        UPDATE portfolio 
                        SET quantity = ?, avg_price = ?, current_price = ?,
                            profit_loss = ?, profit_loss_rate = ?, 
                            last_updated = CURRENT_TIMESTAMP
                        WHERE stock_code = ?
                    """, (new_qty, new_avg, current_price, profit_loss, 
                         profit_loss_rate, stock_code))
            else:
                # 새 포지션 추가
                cursor.execute("""
                    INSERT INTO portfolio (
                        stock_code, quantity, avg_price, current_price
                    ) VALUES (?, ?, ?, ?)
                """, (stock_code, quantity, avg_price, current_price))
            
            conn.commit()
    
    def add_signal(self, signal_data: Dict[str, Any]) -> int:
        """거래 신호 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO signals (
                    stock_code, signal_type, strategy, strength, price, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                signal_data['stock_code'],
                signal_data['signal_type'],
                signal_data['strategy'],
                signal_data.get('strength', 1.0),
                signal_data.get('price'),
                signal_data.get('notes')
            ))
            return cursor.lastrowid
    
    def add_price_data(self, stock_code: str, price_data: Dict[str, Any]):
        """가격 데이터 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO price_data (
                    stock_code, timestamp, open, high, low, close, volume
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                stock_code,
                price_data['timestamp'],
                price_data.get('open'),
                price_data.get('high'),
                price_data.get('low'),
                price_data['close'],
                price_data.get('volume')
            ))
            conn.commit()
    
    def get_price_history(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """가격 이력 조회"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT timestamp, open, high, low, close, volume
                FROM price_data
                WHERE stock_code = ? 
                AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp
            """.format(days)
            return pd.read_sql_query(query, conn, params=(stock_code,))
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """현재 포트폴리오 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stock_code, stock_name, quantity, avg_price, 
                       current_price, profit_loss, profit_loss_rate
                FROM portfolio
                WHERE quantity > 0
            """)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_recent_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 주문 내역 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def calculate_performance(self, date: str = None):
        """성과 계산 및 저장"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 오늘의 거래 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as trades_count,
                    SUM(CASE WHEN executed_price * executed_quantity - price * quantity > 0 
                        THEN 1 ELSE 0 END) as profit_trades,
                    SUM(CASE WHEN executed_price * executed_quantity - price * quantity <= 0 
                        THEN 1 ELSE 0 END) as loss_trades
                FROM orders
                WHERE DATE(executed_at) = ?
                AND status = 'executed'
            """, (date,))
            
            stats = cursor.fetchone()
            trades_count = stats[0] or 0
            profit_trades = stats[1] or 0
            loss_trades = stats[2] or 0
            win_rate = (profit_trades / trades_count * 100) if trades_count > 0 else 0
            
            # 포트폴리오 총 가치
            cursor.execute("""
                SELECT SUM(quantity * current_price) as total_value
                FROM portfolio
                WHERE quantity > 0
            """)
            total_value = cursor.fetchone()[0] or 0
            
            # 성과 저장
            cursor.execute("""
                INSERT OR REPLACE INTO performance (
                    date, total_value, win_rate, trades_count, 
                    profit_trades, loss_trades
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (date, total_value, win_rate, trades_count, 
                 profit_trades, loss_trades))
            
            conn.commit()
    
    def add_log(self, level: str, module: str, message: str, details: str = None):
        """시스템 로그 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (level, module, message, details)
                VALUES (?, ?, ?, ?)
            """, (level, module, message, details))
            conn.commit()

# 전역 데이터베이스 인스턴스
db = TradingDatabase()