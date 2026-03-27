# Crawler & Pipeline 실행 계획
# Spec: docs/specs/2026-03-26-crawler-pipeline.md

## 파일 구조
CREATE  src/crawler/base.py              (베이스 크롤러 추상 클래스)
CREATE  src/crawler/busan_gov.py         (부산시 크롤러)
CREATE  src/crawler/busan_youth.py       (부산청년플랫폼 크롤러)
CREATE  src/pipeline/normalizer.py       (정규화/필드 추출)
CREATE  src/pipeline/chunker.py          (섹션 기반 청킹)
CREATE  src/pipeline/embedder.py         (임베딩 생성, 추상화)
CREATE  src/db/models.py                 (PostgreSQL 스키마)
CREATE  src/db/vector_store.py           (pgvector 인덱스 관리)
CREATE  tests/test_crawler.py
CREATE  tests/test_pipeline.py

## Task 1: DB 스키마 + pgvector 세팅
Files: src/db/models.py, src/db/vector_store.py

[x] Step 1: postings 테이블 + chunks 테이블 모델 작성
[x] Step 2: pgvector extension 활성화 확인
[x] Step 3: 마이그레이션 실행 확인
[x] Step 4: 커밋

## Task 2: 베이스 크롤러 + 부산시 크롤러
Files: src/crawler/base.py, src/crawler/busan_gov.py
      tests/test_crawler.py

[x] Step 1: 실패하는 테스트 작성 (URL 수집, 본문 파싱)
[x] Step 2: 베이스 추상 클래스 구현
[x] Step 3: 부산시 커넥터 구현
[x] Step 4: 테스트 통과 확인
[x] Step 5: 커밋

## Task 3: 부산청년플랫폼 크롤러
Files: src/crawler/busan_youth.py

[x] Step 1: 실패하는 테스트 작성
[x] Step 2: 구현
[x] Step 3: 테스트 통과 확인
[x] Step 4: 커밋

## Task 4: 정규화 파이프라인
Files: src/pipeline/normalizer.py

[x] Step 1: 필드 추출 규칙 기반 구현 (deadline_at 우선)
[x] Step 2: raw_hash 중복 감지 로직
[x] Step 3: 테스트 통과 확인
[x] Step 4: 커밋

## Task 5: 청킹 + 임베딩 + pgvector 저장
Files: src/pipeline/chunker.py, src/pipeline/embedder.py
      src/db/vector_store.py

[x] Step 1: 섹션 기반 청킹 구현
[x] Step 2: 임베딩 추상화 레이어 구현
[x] Step 3: pgvector 인덱스 저장/조회 확인
[x] Step 4: 전체 파이프라인 통합 테스트
[x] Step 5: 커밋
