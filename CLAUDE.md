# Public-Notice-Bot

## 프로젝트 개요
부산 지역 학생/취준생 대상 공고·제도 정보를 자동 수집·정규화하고,
사용자 조건에 맞게 필터링 + 요약 + QA 해주는 RAG 기반 챗봇 서비스

## 기술 스택
- Backend: Python 3.11, FastAPI, Pydantic
- DB: PostgreSQL + pgvector
- Crawler: httpx, BeautifulSoup4, Playwright(JS 렌더링 필요 시)
- Queue: Redis + Celery
- LLM: OpenAI API (GPT-4o-mini 기본, 교체 가능하게 추상화)
- Frontend: React 18 + Vite
- 배포: Docker + docker-compose

## 폴더 구조
- src/crawler/     : 사이트별 크롤러 모듈
- src/pipeline/    : 정규화/추출/청킹/임베딩
- src/api/         : FastAPI 라우터
- src/rag/         : Retriever, Reranker, Generator
- src/recommender/ : 추천/랭킹 로직
- frontend/        : React + Vite
- tests/           : 테스트
- docs/specs/      : 기능별 스펙
- docs/plans/      : 실행 계획

## 코딩 규칙
- 기본 언어: Python
- 타입 힌트 -> 사용 금지
- 주석 작성 금지
- sys.stdin.readline() 사용

## 경계선
- [OK]  새 파일 생성, 로직 수정, 크롤러 추가
- [ASK] 폴더 구조 변경, 외부 라이브러리 추가, DB 스키마 변경
- [NO]  .env 파일 수정, 기존 테스트 삭제, LLM 추상화 레이어 제거