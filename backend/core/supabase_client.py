"""
Supabase 클라이언트 설정
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Supabase 설정
SUPABASE_URL = os.getenv('VITE_SUPABASE_URL', 'https://hznkyaomtrpzcayayayh.supabase.co')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bmt5YW9tdHJwemNheWF5YXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3ODg1MTQsImV4cCI6MjA0ODM2NDUxNH0.YCDh1cBp5hBnT0mmDG8dDvEaM2UWQ3xb4Hp9fXZvJOI')

# 전역 Supabase 클라이언트
_supabase_client = None

def get_supabase_client() -> Client:
    """
    Supabase 클라이언트 인스턴스를 반환합니다.
    싱글톤 패턴으로 구현되어 있습니다.
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    return _supabase_client

def init_supabase() -> Client:
    """
    Supabase 클라이언트를 초기화합니다.
    """
    return get_supabase_client()