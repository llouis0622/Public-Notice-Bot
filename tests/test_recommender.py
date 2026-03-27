import pytest
from datetime import datetime, timezone

from src.recommender.ranker import rank_postings, score_posting


BASE_DATE = datetime(2024, 3, 15, tzinfo=timezone.utc)

POSTINGS = [
    {
        "id": "a",
        "title": "부산청년 장학금",
        "category": "장학금",
        "deadline_at": datetime(2024, 3, 20, tzinfo=timezone.utc),
        "eligibility_text": "부산 거주 대학생 만 19~39세",
        "region": "부산",
    },
    {
        "id": "b",
        "title": "청년 창업 지원",
        "category": "인턴",
        "deadline_at": datetime(2024, 4, 30, tzinfo=timezone.utc),
        "eligibility_text": "만 19~34세 청년",
        "region": "부산",
    },
    {
        "id": "c",
        "title": "취업 교육 프로그램",
        "category": "교육",
        "deadline_at": datetime(2024, 2, 28, tzinfo=timezone.utc),
        "eligibility_text": "취업 준비생",
        "region": "부산",
    },
    {
        "id": "d",
        "title": "전국 공모전",
        "category": "대외활동",
        "deadline_at": datetime(2024, 5, 31, tzinfo=timezone.utc),
        "eligibility_text": "대학생",
        "region": "서울",
    },
]

USER_PROFILE = {
    "age": 24,
    "categories": ["장학금", "교육"],
    "region": "부산",
}


def test_rank_postings_returns_list():
    result = rank_postings(POSTINGS, USER_PROFILE, now=BASE_DATE)
    assert isinstance(result, list)


def test_rank_postings_preserves_all_items():
    result = rank_postings(POSTINGS, USER_PROFILE, now=BASE_DATE)
    assert len(result) == len(POSTINGS)


def test_rank_postings_expired_scored_lower():
    result = rank_postings(POSTINGS, USER_PROFILE, now=BASE_DATE)
    ids = [r["id"] for r in result]
    expired_idx = ids.index("c")
    active_idx = ids.index("a")
    assert active_idx < expired_idx


def test_rank_postings_preferred_category_ranked_higher():
    result = rank_postings(POSTINGS, USER_PROFILE, now=BASE_DATE)
    ids = [r["id"] for r in result]
    scholarship_idx = ids.index("a")
    startup_idx = ids.index("b")
    assert scholarship_idx < startup_idx


def test_rank_postings_same_region_ranked_higher():
    result = rank_postings(POSTINGS, USER_PROFILE, now=BASE_DATE)
    ids = [r["id"] for r in result]
    busan_idx = ids.index("b")
    seoul_idx = ids.index("d")
    assert busan_idx < seoul_idx


def test_rank_postings_adds_score_field():
    result = rank_postings(POSTINGS, USER_PROFILE, now=BASE_DATE)
    for r in result:
        assert "score" in r


def test_score_posting_preferred_category_gets_bonus():
    profile = {"age": 24, "categories": ["장학금"], "region": "부산"}
    s1 = score_posting(POSTINGS[0], profile, now=BASE_DATE)
    s2 = score_posting(POSTINGS[1], profile, now=BASE_DATE)
    assert s1 > s2


def test_score_posting_expired_gets_zero():
    profile = {"age": 24, "categories": [], "region": "부산"}
    score = score_posting(POSTINGS[2], profile, now=BASE_DATE)
    assert score == 0


def test_rank_postings_empty_profile_still_works():
    result = rank_postings(POSTINGS, {}, now=BASE_DATE)
    assert len(result) == len(POSTINGS)


def test_rank_postings_no_deadline_not_penalized():
    postings = [{"id": "x", "title": "마감없는공고", "category": "정책",
                 "deadline_at": None, "eligibility_text": "", "region": "부산"}]
    result = rank_postings(postings, USER_PROFILE, now=BASE_DATE)
    assert result[0]["score"] >= 0
