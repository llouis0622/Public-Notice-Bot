# Crawler & Pipeline Spec

## 목적
부산 지역 공고 소스 5~10개를 자동 수집하고,
정규화된 스키마로 PostgreSQL에 저장한다.
RAG QA를 위한 청킹 + 임베딩까지 완료하는 것이 목표.

## 타깃 소스 (MVP)
- 부산시 공식 홈페이지 (www.busan.go.kr)
- 부산청년플랫폼 (youth.busan.go.kr)
- 워크넷 부산 지역 필터
- 부산테크노파크
- 경성대학교 공지사항 (취업/장학)

## 요구사항
- 소스별 독립 커넥터 모듈로 구성 (사이트 추가/제거 용이)
- 증분 업데이트: 본문 해시로 중복/변경 감지
- robots.txt 준수, 도메인별 요청 딜레이 적용
- 수집 실패 시 재시도 로직 포함

## 정규화 스키마 (필수 필드)
- id, source, url, title, organization
- category (장학금/인턴/교육/정책/채용/대외활동)
- region, eligibility_text, benefits_text
- requirements_text, apply_method_text
- deadline_at, start_at, end_at
- raw_hash, created_at, updated_at

## 청킹 전략
- 섹션 단위: 지원자격 / 신청방법 / 혜택 / 마감일 / 기타
- chunk_type 필드로 구분하여 저장
- 각 chunk에 source_span(원문 위치) 포함

## 성공 기준
- 소스 5개 이상 수집 완료
- 정규화 필드 누락률 20% 이하 (deadline_at 기준)
- 중복 공고 DB 저장 안 됨
- 임베딩 생성 후 pgvector 인덱스 정상 조회

## 기술적 제약
- Playwright는 JS 렌더링 필요한 소스만 사용 (비용/속도)
- LLM extraction은 규칙 기반 실패 시에만 fallback으로 사용
- 임베딩 모델은 추상화 레이어로 교체 가능하게 구성

## 경계선
- [OK]  크롤러 모듈 추가, 청킹 로직 수정
- [ASK] DB 스키마 필드 추가, 임베딩 모델 교체
- [NO]  raw_hash 중복 감지 로직 제거, source_span 없는 chunk 저장