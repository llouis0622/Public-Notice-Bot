import pytest
import hashlib

from src.pipeline.normalizer import normalize, compute_hash, is_duplicate


RAW_BUSAN_GOV = {
    "source": "busan_gov",
    "url": "https://www.busan.go.kr/noticeView?ntcId=AAA001",
    "title": "2024년 부산청년 장학금 모집",
    "organization": "부산광역시",
    "deadline_at": "2024-03-31",
    "raw_content": "신청기간: 2024-03-01 ~ 2024-03-31\n지원자격: 부산 거주 대학생\n지원내용: 학비 최대 200만원\n신청방법: 온라인 접수",
}

RAW_BUSAN_YOUTH = {
    "source": "busan_youth",
    "url": "https://youth.busan.go.kr/youth/program/view?seq=101",
    "title": "청년 창업 지원 프로그램",
    "organization": "부산광역시 청년정책과",
    "deadline_at": "2024-04-15",
    "raw_content": "주관기관: 부산광역시 청년정책과\n신청기간: 2024-03-01 ~ 2024-04-15\n지원자격: 만 19~39세\n지원내용: 창업 자금 1000만원",
}

RAW_MINIMAL = {
    "source": "busan_gov",
    "url": "https://www.busan.go.kr/noticeView?ntcId=BBB001",
    "title": "간단 공고",
    "raw_content": "",
}


def test_normalize_returns_dict_with_required_keys():
    result = normalize(RAW_BUSAN_GOV)
    for key in ("source", "url", "title", "raw_hash"):
        assert key in result, f"Missing key: {key}"


def test_normalize_sets_raw_hash():
    result = normalize(RAW_BUSAN_GOV)
    assert len(result["raw_hash"]) == 64


def test_normalize_raw_hash_is_sha256_of_content():
    result = normalize(RAW_BUSAN_GOV)
    expected = hashlib.sha256(RAW_BUSAN_GOV["raw_content"].encode()).hexdigest()
    assert result["raw_hash"] == expected


def test_normalize_deadline_at_parsed_to_datetime():
    from datetime import datetime
    result = normalize(RAW_BUSAN_GOV)
    assert isinstance(result["deadline_at"], datetime)


def test_normalize_missing_deadline_is_none():
    result = normalize(RAW_MINIMAL)
    assert result["deadline_at"] is None


def test_normalize_extracts_eligibility_from_content():
    result = normalize(RAW_BUSAN_GOV)
    assert result.get("eligibility_text") is not None
    assert "부산" in result["eligibility_text"]


def test_normalize_extracts_benefits_from_content():
    result = normalize(RAW_BUSAN_GOV)
    assert result.get("benefits_text") is not None
    assert "200만원" in result["benefits_text"]


def test_normalize_extracts_apply_method_from_content():
    result = normalize(RAW_BUSAN_GOV)
    assert result.get("apply_method_text") is not None
    assert "온라인" in result["apply_method_text"]


def test_normalize_category_detected_for_scholarship():
    result = normalize(RAW_BUSAN_GOV)
    assert result.get("category") == "장학금"


def test_normalize_category_detected_for_startup():
    result = normalize(RAW_BUSAN_YOUTH)
    assert result.get("category") == "인턴"


def test_normalize_region_defaults_to_busan():
    result = normalize(RAW_BUSAN_GOV)
    assert result.get("region") == "부산"


def test_compute_hash_same_content_same_hash():
    h1 = compute_hash("hello")
    h2 = compute_hash("hello")
    assert h1 == h2


def test_compute_hash_different_content_different_hash():
    h1 = compute_hash("hello")
    h2 = compute_hash("world")
    assert h1 != h2


def test_is_duplicate_true_when_hash_in_set():
    existing = {"abc123", "def456"}
    assert is_duplicate("abc123", existing) is True


def test_is_duplicate_false_when_hash_not_in_set():
    existing = {"abc123"}
    assert is_duplicate("xyz789", existing) is False
