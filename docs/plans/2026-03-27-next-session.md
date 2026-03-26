# 내일 세션 시작 가이드
# 작성일: 2026-03-26

## 현재 완료된 것
- Task 1: DB 스키마 + pgvector 세팅 완료
  - src/db/models.py: postings / chunks 테이블
  - src/db/vector_store.py: pgvector 인덱스 관리
  - src/db/migrate.py: 마이그레이션 스크립트
  - docker-compose.yml: PostgreSQL(pgvector) + Redis

## 내일 할 것
- docs/plans/2026-03-26-crawler-pipeline.md Task 2부터 시작

## 환경 시작 명령어
```bash
cd ~/Desktop/LLouis/Public-Notice-Bot
docker compose up -d
```

## DB 접속 정보
- Host: localhost:5433
- DB: public_notice_bot
- User: notice_user
- Pass: notice_pass
- DATABASE_URL: postgresql://notice_user:notice_pass@localhost:5433/public_notice_bot

## 주의사항
- .env 파일에 DATABASE_URL 설정 필요 (아직 미설정 상태)
- 로컬 PostgreSQL(Homebrew)이 5432 점유 중 → Docker는 5433 사용
