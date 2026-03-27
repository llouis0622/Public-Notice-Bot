# 세션 가이드
# 작성일: 2026-03-27

## 현재 완료된 것
- Task 1: DB 스키마 + pgvector 세팅
- Task 2: 베이스 크롤러 + 부산시 크롤러
- Task 3: 부산청년플랫폼 크롤러
- Task 4: 정규화 파이프라인
- Task 5: 청킹 + 임베딩 파이프라인
- Task 6: RAG 레이어 (Retriever, Reranker, Generator)
- Task 7: FastAPI 라우터 (chat, postings, crawl, recommend)
- Task 8: Celery 태스크 + Recommender
- Task 9: 프론트엔드 (React + Vite)
  - 공고 목록 페이지 (카테고리 필터)
  - 챗봇 페이지 (RAG 연동)
  - 맞춤 추천 페이지 (나이/지역/관심분야)

## 남은 작업
- 통합 테스트 (백엔드 + 프론트 E2E)
- Docker compose에 프론트엔드 빌드 추가 (선택)
- 실제 크롤링 데이터로 동작 확인

## 환경 시작 명령어
```bash
# DB + Redis
docker compose up -d

# FastAPI
uvicorn src.api.main:app --reload --port 8000

# Celery (필요 시)
celery -A src.tasks.celery_app worker --loglevel=info

# 프론트엔드
cd frontend && npm run dev
```

## DB 접속 정보
- Host: localhost:5433
- DB: public_notice_bot
- User: notice_user
- Pass: notice_pass
- DATABASE_URL: postgresql://notice_user:notice_pass@localhost:5433/public_notice_bot

## 주의사항
- .env 파일에 OPENAI_API_KEY, DATABASE_URL 설정 필요
- 로컬 PostgreSQL(Homebrew)이 5432 점유 중 → Docker는 5433 사용
- 프론트 vite proxy → 백엔드 8000 포트 포워딩 설정됨 (CORS 불필요)
