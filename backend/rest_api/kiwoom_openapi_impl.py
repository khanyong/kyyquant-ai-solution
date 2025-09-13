"""
키움증권 OpenAPI+ 구현체 (Windows 전용)
COM 객체를 통한 실시간 거래 지원
"""

import sys
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from kiwoom_api_interface import KiwoomAPIInterface, StockPrice, OrderResult, Balance

logger = logging.getLogger(__name__)

# Windows 환경에서만 import
if sys.platform == 'win32':
    try:
        import win32com.client
        import pythoncom
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QEventLoop
        OPENAPI_AVAILABLE = True
    except ImportError:
        OPENAPI_AVAILABLE = False
        logger.warning("OpenAPI+ 모듈을 찾을 수 없습니다. REST API를 사용하세요.")
else:
    OPENAPI_AVAILABLE = False

class KiwoomOpenAPI(KiwoomAPIInterface):
    """키움 OpenAPI+ 구현체"""
    
    def __init__(self):
        if not OPENAPI_AVAILABLE:
            raise RuntimeError("OpenAPI+는 Windows에서만 사용 가능합니다.")
        
        self.ocx = None
        self.connected = False
        self.app = None
        self.account_no = None
        self.realtime_callbacks = {}
        
    async def connect(self) -> bool:
        """OpenAPI+ 연결"""
        try:
            # Qt 이벤트 루프 초기화
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            
            # COM 객체 생성
            pythoncom.CoInitialize()
            self.ocx = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
            
            # 이벤트 핸들러 연결
            self._setup_event_handlers()
            
            # 로그인
            login_result = self.ocx.CommConnect()
            if login_result != 0:
                logger.error("OpenAPI+ 로그인 실패")
                return False
            
            # 로그인 대기 (최대 30초)
            for _ in range(30):
                if self.connected:
                    break
                await asyncio.sleep(1)
                QApplication.processEvents()
            
            if self.connected:
                # 계좌 정보 가져오기
                self.account_no = self.ocx.GetLoginInfo("ACCNO").split(';')[0]
                logger.info(f"OpenAPI+ 연결 성공. 계좌: {self.account_no}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"OpenAPI+ 연결 실패: {e}")
            return False
    
    def _setup_event_handlers(self):
        """이벤트 핸들러 설정"""
        # 로그인 이벤트
        self.ocx.OnEventConnect.connect(self._on_connect)
        # 조회 응답
        self.ocx.OnReceiveTrData.connect(self._on_receive_tr_data)
        # 실시간 데이터
        self.ocx.OnReceiveRealData.connect(self._on_receive_real_data)
        # 주문 응답
        self.ocx.OnReceiveChejanData.connect(self._on_receive_chejan_data)
    
    def _on_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            self.connected = True
            logger.info("OpenAPI+ 로그인 성공")
        else:
            logger.error(f"OpenAPI+ 로그인 실패: {err_code}")
    
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next):
        """TR 데이터 수신"""
        # 요청별로 처리
        pass
    
    def _on_receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신"""
        if code in self.realtime_callbacks:
            callback = self.realtime_callbacks[code]
            # 실시간 데이터 파싱
            data = self._parse_real_data(code, real_type, real_data)
            callback(data)
    
    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결 데이터 수신"""
        pass
    
    def _parse_real_data(self, code, real_type, real_data) -> Dict:
        """실시간 데이터 파싱"""
        return {
            'code': code,
            'type': real_type,
            'price': self.ocx.GetCommRealData(code, 10),
            'volume': self.ocx.GetCommRealData(code, 15),
            'time': self.ocx.GetCommRealData(code, 20),
            'timestamp': datetime.now().isoformat()
        }
    
    async def disconnect(self) -> bool:
        """연결 해제"""
        try:
            if self.ocx:
                self.ocx.CommTerminate()
            self.connected = False
            pythoncom.CoUninitialize()
            return True
        except Exception as e:
            logger.error(f"연결 해제 실패: {e}")
            return False
    
    async def get_current_price(self, stock_code: str) -> Optional[StockPrice]:
        """현재가 조회"""
        try:
            self.ocx.SetInputValue("종목코드", stock_code)
            ret = self.ocx.CommRqData("주식기본정보", "opt10001", 0, "0101")
            
            if ret != 0:
                logger.error(f"현재가 조회 실패: {stock_code}")
                return None
            
            # 응답 대기
            await asyncio.sleep(0.5)
            
            return StockPrice(
                code=stock_code,
                name=self.ocx.GetCommData("opt10001", "주식기본정보", 0, "종목명").strip(),
                price=abs(int(self.ocx.GetCommData("opt10001", "주식기본정보", 0, "현재가"))),
                change=int(self.ocx.GetCommData("opt10001", "주식기본정보", 0, "전일대비")),
                change_rate=float(self.ocx.GetCommData("opt10001", "주식기본정보", 0, "등락율")),
                volume=int(self.ocx.GetCommData("opt10001", "주식기본정보", 0, "거래량")),
                high=abs(int(self.ocx.GetCommData("opt10001", "주식기본정보", 0, "고가"))),
                low=abs(int(self.ocx.GetCommData("opt10001", "주식기본정보", 0, "저가"))),
                open=abs(int(self.ocx.GetCommData("opt10001", "주식기본정보", 0, "시가"))),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"현재가 조회 오류: {e}")
            return None
    
    async def get_ohlcv(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """일봉 데이터 조회"""
        try:
            self.ocx.SetInputValue("종목코드", stock_code)
            self.ocx.SetInputValue("기준일자", end_date)
            self.ocx.SetInputValue("수정주가구분", "1")
            
            ret = self.ocx.CommRqData("일봉차트조회", "opt10081", 0, "0102")
            if ret != 0:
                return []
            
            await asyncio.sleep(0.5)
            
            data_list = []
            count = self.ocx.GetRepeatCnt("opt10081", "일봉차트조회")
            
            for i in range(count):
                date = self.ocx.GetCommData("opt10081", "일봉차트조회", i, "일자").strip()
                if date < start_date:
                    break
                    
                data_list.append({
                    'date': date,
                    'open': abs(int(self.ocx.GetCommData("opt10081", "일봉차트조회", i, "시가"))),
                    'high': abs(int(self.ocx.GetCommData("opt10081", "일봉차트조회", i, "고가"))),
                    'low': abs(int(self.ocx.GetCommData("opt10081", "일봉차트조회", i, "저가"))),
                    'close': abs(int(self.ocx.GetCommData("opt10081", "일봉차트조회", i, "현재가"))),
                    'volume': int(self.ocx.GetCommData("opt10081", "일봉차트조회", i, "거래량"))
                })
            
            return data_list
            
        except Exception as e:
            logger.error(f"일봉 데이터 조회 오류: {e}")
            return []
    
    async def get_balance(self) -> Optional[Balance]:
        """계좌 잔고 조회"""
        try:
            self.ocx.SetInputValue("계좌번호", self.account_no)
            self.ocx.SetInputValue("비밀번호", "")
            self.ocx.SetInputValue("비밀번호입력매체구분", "00")
            self.ocx.SetInputValue("조회구분", "1")
            
            ret = self.ocx.CommRqData("계좌평가잔고내역", "opw00018", 0, "0103")
            if ret != 0:
                return None
            
            await asyncio.sleep(0.5)
            
            # 계좌 정보
            total_eval = int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", 0, "총평가금액"))
            total_purchase = int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", 0, "총매입금액"))
            total_profit = int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", 0, "총평가손익금액"))
            cash = int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", 0, "예수금"))
            
            # 보유 종목
            holdings = []
            count = self.ocx.GetRepeatCnt("opw00018", "계좌평가잔고내역")
            
            for i in range(count):
                holdings.append({
                    'code': self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "종목번호").strip(),
                    'name': self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "종목명").strip(),
                    'quantity': int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "보유수량")),
                    'avg_price': float(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "매입가")),
                    'current_price': int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "현재가")),
                    'eval_amount': int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "평가금액")),
                    'profit_loss': int(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "평가손익")),
                    'profit_rate': float(self.ocx.GetCommData("opw00018", "계좌평가잔고내역", i, "수익률(%)"))
                })
            
            return Balance(
                total_eval=total_eval,
                total_purchase=total_purchase,
                total_profit=total_profit,
                cash=cash,
                holdings=holdings,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"잔고 조회 오류: {e}")
            return None
    
    async def place_order(
        self, 
        stock_code: str, 
        quantity: int, 
        price: int, 
        order_type: str = 'buy',
        order_method: str = 'limit'
    ) -> Optional[OrderResult]:
        """주문 실행"""
        try:
            # 주문 타입 설정
            if order_type == 'buy':
                order_type_code = 1  # 신규매수
            else:
                order_type_code = 2  # 신규매도
            
            # 호가 구분
            if order_method == 'market':
                price_type = "03"  # 시장가
                price = 0
            else:
                price_type = "00"  # 지정가
            
            ret = self.ocx.SendOrder(
                "주문",  # 사용자 구분명
                "0104",  # 화면번호
                self.account_no,  # 계좌번호
                order_type_code,  # 주문유형
                stock_code,  # 종목코드
                quantity,  # 주문수량
                price,  # 주문가격
                price_type,  # 호가구분
                ""  # 원주문번호 (정정/취소시 사용)
            )
            
            if ret == 0:
                return OrderResult(
                    success=True,
                    order_no="",  # 체결 이벤트에서 받음
                    message="주문 전송 성공",
                    timestamp=datetime.now(),
                    details={'code': stock_code, 'quantity': quantity, 'price': price}
                )
            else:
                return OrderResult(
                    success=False,
                    order_no="",
                    message=f"주문 전송 실패: {ret}",
                    timestamp=datetime.now(),
                    details={}
                )
                
        except Exception as e:
            logger.error(f"주문 실행 오류: {e}")
            return None
    
    async def cancel_order(self, order_no: str) -> Optional[OrderResult]:
        """주문 취소"""
        # SendOrder with 취소 타입 사용
        pass
    
    async def get_order_history(self, start_date: str = None) -> List[Dict]:
        """주문 내역 조회"""
        # opt10075 TR 사용
        pass
    
    async def subscribe_realtime(self, stock_codes: List[str], callback: callable):
        """실시간 시세 구독"""
        try:
            # 실시간 등록
            for code in stock_codes:
                self.realtime_callbacks[code] = callback
                
            # 실시간 데이터 요청
            fid_list = "10;11;12;13;14;15"  # 현재가, 거래량 등
            self.ocx.SetRealReg("0150", ";".join(stock_codes), fid_list, "0")
            
            logger.info(f"실시간 구독: {stock_codes}")
            
        except Exception as e:
            logger.error(f"실시간 구독 오류: {e}")
    
    async def unsubscribe_realtime(self, stock_codes: List[str]):
        """실시간 구독 해제"""
        try:
            for code in stock_codes:
                if code in self.realtime_callbacks:
                    del self.realtime_callbacks[code]
            
            self.ocx.SetRealRemove("0150", ";".join(stock_codes))
            logger.info(f"실시간 구독 해제: {stock_codes}")
            
        except Exception as e:
            logger.error(f"실시간 구독 해제 오류: {e}")
    
    @property
    def is_connected(self) -> bool:
        return self.connected
    
    @property
    def api_type(self) -> str:
        return "openapi"
    
    @property
    def platform(self) -> str:
        return "windows"