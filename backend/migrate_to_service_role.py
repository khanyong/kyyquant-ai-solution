"""
백엔드 파일들을 SUPABASE_ANON_KEY에서 SUPABASE_SERVICE_ROLE_KEY로 마이그레이션
"""
import os
import re
from pathlib import Path

def migrate_file(file_path: Path):
    """파일의 Supabase 키 참조를 Service Role로 변경"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 패턴 1: os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        # → os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        content = re.sub(
            r"os\.getenv\('SUPABASE_KEY'\)\s*or\s*os\.getenv\('SUPABASE_ANON_KEY'\)",
            "os.getenv('SUPABASE_SERVICE_ROLE_KEY')",
            content
        )

        # 패턴 2: os.getenv('SUPABASE_ANON_KEY')
        # → os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        content = re.sub(
            r"os\.getenv\('SUPABASE_ANON_KEY'\)",
            "os.getenv('SUPABASE_SERVICE_ROLE_KEY')",
            content
        )

        # 패턴 3: os.getenv('SUPABASE_KEY')
        # → os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        content = re.sub(
            r"os\.getenv\('SUPABASE_KEY'\)(?!\s*or)",
            "os.getenv('SUPABASE_SERVICE_ROLE_KEY')",
            content
        )

        # 패턴 4: 환경 변수 문서화 주석 업데이트
        content = re.sub(
            r"SUPABASE_KEY must be set",
            "SUPABASE_SERVICE_ROLE_KEY must be set",
            content
        )

        # 패턴 5: 로그 메시지 업데이트
        content = re.sub(
            r"'SUPABASE_KEY':",
            "'SUPABASE_SERVICE_ROLE_KEY':",
            content
        )

        # 변경사항이 있으면 파일 업데이트
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated: {file_path}")
            return True
        else:
            print(f"[SKIP] Skipped (no changes): {file_path}")
            return False

    except Exception as e:
        print(f"[ERROR] Error processing {file_path}: {e}")
        return False

def migrate_docker_compose(file_path: Path):
    """Docker Compose 파일의 환경 변수 업데이트"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # SUPABASE_KEY를 SUPABASE_SERVICE_ROLE_KEY로 변경
        content = re.sub(
            r"- SUPABASE_KEY=\$\{SUPABASE_KEY\}",
            "- SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}",
            content
        )

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated Docker Compose: {file_path}")
            return True
        else:
            print(f"[SKIP] Skipped Docker Compose (no changes): {file_path}")
            return False

    except Exception as e:
        print(f"[ERROR] Error processing {file_path}: {e}")
        return False

def main():
    """모든 백엔드 파일 마이그레이션"""
    backend_dir = Path(__file__).parent

    print("[*] Starting migration to SUPABASE_SERVICE_ROLE_KEY...\n")

    # Python 파일들
    python_files = list(backend_dir.rglob("*.py"))
    python_files = [f for f in python_files if 'venv' not in str(f) and 'migrate_to_service_role.py' not in str(f)]

    updated_count = 0
    for py_file in python_files:
        if migrate_file(py_file):
            updated_count += 1

    # Docker Compose 파일들
    docker_files = [
        backend_dir / "docker-compose.yml",
        backend_dir / "docker-compose.synology.yml"
    ]

    for docker_file in docker_files:
        if docker_file.exists():
            if migrate_docker_compose(docker_file):
                updated_count += 1

    print(f"\n[DONE] Migration complete! Updated {updated_count} files.")
    print("\n[!] Next steps:")
    print("1. .env 파일에 SUPABASE_SERVICE_ROLE_KEY 추가")
    print("2. Supabase Dashboard에서 Service Role Key 복사")
    print("3. 모든 배포 환경의 환경 변수 업데이트")

if __name__ == "__main__":
    main()
