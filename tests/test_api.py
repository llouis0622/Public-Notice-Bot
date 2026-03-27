import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_chat_returns_200(client):
    mock_answer = "부산 거주 대학생이면 신청 가능합니다."
    with patch("src.api.routes.chat.get_rag_pipeline") as mock_pipeline:
        mock_pipeline.return_value.answer.return_value = mock_answer
        resp = client.post("/chat", json={"query": "장학금 신청 자격이 뭔가요?"})
    assert resp.status_code == 200


def test_chat_returns_answer_field(client):
    mock_answer = "부산 거주 대학생이면 신청 가능합니다."
    with patch("src.api.routes.chat.get_rag_pipeline") as mock_pipeline:
        mock_pipeline.return_value.answer.return_value = mock_answer
        resp = client.post("/chat", json={"query": "장학금 신청 자격이 뭔가요?"})
    assert "answer" in resp.json()
    assert resp.json()["answer"] == mock_answer


def test_chat_missing_query_returns_422(client):
    resp = client.post("/chat", json={})
    assert resp.status_code == 422


def test_chat_empty_query_returns_400(client):
    with patch("src.api.routes.chat.get_rag_pipeline"):
        resp = client.post("/chat", json={"query": ""})
    assert resp.status_code == 400


def test_postings_returns_200(client):
    with patch("src.api.routes.postings.get_db_session") as mock_session:
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)
        with patch("src.api.routes.postings.fetch_postings", return_value=[]):
            resp = client.get("/postings")
    assert resp.status_code == 200


def test_postings_returns_list(client):
    mock_posting = {
        "id": "uuid-1",
        "source": "busan_gov",
        "title": "장학금 모집",
        "category": "장학금",
        "deadline_at": None,
        "url": "https://www.busan.go.kr/noticeView?ntcId=AAA001",
    }
    with patch("src.api.routes.postings.get_db_session") as mock_session:
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)
        with patch("src.api.routes.postings.fetch_postings", return_value=[mock_posting]):
            resp = client.get("/postings")
    assert isinstance(resp.json(), list)


def test_postings_filter_by_category(client):
    with patch("src.api.routes.postings.get_db_session") as mock_session:
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)
        with patch("src.api.routes.postings.fetch_postings", return_value=[]) as mock_fetch:
            resp = client.get("/postings?category=장학금")
    assert resp.status_code == 200
    _, kwargs = mock_fetch.call_args
    assert kwargs.get("category") == "장학금"


def test_crawl_trigger_returns_202(client):
    with patch("src.api.routes.crawl.trigger_crawl") as mock_trigger:
        mock_trigger.return_value = {"queued": ["busan_gov"]}
        resp = client.post("/crawl", json={"sources": ["busan_gov"]})
    assert resp.status_code == 202


def test_crawl_trigger_unknown_source_returns_400(client):
    resp = client.post("/crawl", json={"sources": ["unknown_source"]})
    assert resp.status_code == 400
