"""
잔고 동기화 서비스 실행 스크립트
백그라운드에서 WebSocket 연결을 유지하며 실시간 잔고 데이터를 DB에 저장
"""

import asyncio
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.balance_sync_service import run_balance_sync_service


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('balance_sync.log')
        ]
    )


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 키움 잔고 동기화 서비스 시작")
    print("=" * 80)

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # .env 파일 로드
        from dotenv import load_dotenv
        env_path = backend_dir / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"✅ .env 파일 로드: {env_path}")
        else:
            logger.warning(f"⚠️ .env 파일 없음: {env_path}")

        # 서비스 실행
        asyncio.run(run_balance_sync_service())

    except KeyboardInterrupt:
        logger.info("\n⏹️ 사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"❌ 서비스 실행 오류: {e}", exc_info=True)
        sys.exit(1)
