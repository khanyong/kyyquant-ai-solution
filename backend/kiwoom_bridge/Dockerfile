FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트 (curl 추가)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 포트 노출
EXPOSE 8001

# 실행 명령 (로그 레벨 추가)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--log-level", "debug"]