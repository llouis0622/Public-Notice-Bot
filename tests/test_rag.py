import pytest
from unittest.mock import patch, MagicMock

from src.rag.retriever import Retriever
from src.rag.reranker import Reranker
from src.rag.generator import Generator


MOCK_CHUNKS = [
    {
        "id": "uuid-1",
        "posting_id": "p-uuid-1",
        "chunk_type": "지원자격",
        "content": "부산 거주 대학생 (만 19~39세)",
        "source_span_start": 0,
        "source_span_end": 20,
        "distance": 0.12,
    },
    {
        "id": "uuid-2",
        "posting_id": "p-uuid-2",
        "chunk_type": "혜택",
        "content": "학비 최대 200만원 지원",
        "source_span_start": 21,
        "source_span_end": 40,
        "distance": 0.25,
    },
    {
        "id": "uuid-3",
        "posting_id": "p-uuid-3",
        "chunk_type": "신청방법",
        "content": "온라인 접수 (부산청년플랫폼 홈페이지)",
        "source_span_start": 41,
        "source_span_end": 70,
        "distance": 0.38,
    },
]


def test_retriever_search_returns_list():
    mock_session = MagicMock()
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = [0.1] * 1536

    mock_rows = [MagicMock(**c) for c in MOCK_CHUNKS]
    mock_rows = []
    for c in MOCK_CHUNKS:
        row = MagicMock()
        row._mapping = c
        mock_rows.append(row)

    with patch("src.rag.retriever.search_similar_chunks", return_value=mock_rows):
        retriever = Retriever(session=mock_session, embedder=mock_embedder)
        results = retriever.search("장학금 신청 자격")
    assert isinstance(results, list)


def test_retriever_search_embeds_query():
    mock_session = MagicMock()
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = [0.1] * 1536

    with patch("src.rag.retriever.search_similar_chunks", return_value=[]):
        retriever = Retriever(session=mock_session, embedder=mock_embedder)
        retriever.search("장학금 신청 자격")
    mock_embedder.embed.assert_called_once_with("장학금 신청 자격")


def test_retriever_search_respects_top_k():
    mock_session = MagicMock()
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = [0.1] * 1536

    with patch("src.rag.retriever.search_similar_chunks", return_value=[]) as mock_search:
        retriever = Retriever(session=mock_session, embedder=mock_embedder)
        retriever.search("질문", top_k=5)
    _, kwargs = mock_search.call_args
    assert kwargs.get("top_k") == 5 or mock_search.call_args[0][2] == 5


def test_retriever_returns_dicts():
    mock_session = MagicMock()
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = [0.1] * 1536

    mock_rows = []
    for c in MOCK_CHUNKS:
        row = MagicMock()
        row._mapping = c
        mock_rows.append(row)

    with patch("src.rag.retriever.search_similar_chunks", return_value=mock_rows):
        retriever = Retriever(session=mock_session, embedder=mock_embedder)
        results = retriever.search("장학금")
    assert all(isinstance(r, dict) for r in results)


def test_reranker_returns_same_length():
    reranker = Reranker()
    results = reranker.rerank("장학금 신청 자격", MOCK_CHUNKS)
    assert len(results) == len(MOCK_CHUNKS)


def test_reranker_returns_sorted_by_score():
    reranker = Reranker()
    results = reranker.rerank("부산 거주 대학생 지원자격", MOCK_CHUNKS)
    scores = [r["rerank_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_reranker_adds_rerank_score():
    reranker = Reranker()
    results = reranker.rerank("장학금", MOCK_CHUNKS)
    for r in results:
        assert "rerank_score" in r


def test_reranker_top_k_limits_results():
    reranker = Reranker()
    results = reranker.rerank("장학금", MOCK_CHUNKS, top_k=2)
    assert len(results) == 2


def test_generator_builds_prompt_with_chunks():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="답변입니다."))]
    mock_client.chat.completions.create.return_value = mock_response

    generator = Generator(client=mock_client)
    answer = generator.generate("장학금 신청 자격이 뭔가요?", MOCK_CHUNKS)
    assert answer == "답변입니다."


def test_generator_calls_openai_with_chunks():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="답변"))]
    mock_client.chat.completions.create.return_value = mock_response

    generator = Generator(client=mock_client)
    generator.generate("질문", MOCK_CHUNKS)

    assert mock_client.chat.completions.create.called
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    user_content = next(m["content"] for m in messages if m["role"] == "user")
    assert "질문" in user_content


def test_generator_includes_chunk_content_in_prompt():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="답변"))]
    mock_client.chat.completions.create.return_value = mock_response

    generator = Generator(client=mock_client)
    generator.generate("질문", MOCK_CHUNKS)

    call_kwargs = mock_client.chat.completions.create.call_args[1]
    all_content = " ".join(m["content"] for m in call_kwargs["messages"])
    assert "부산 거주 대학생" in all_content


def test_generator_returns_string():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="문자열 답변"))]
    mock_client.chat.completions.create.return_value = mock_response

    generator = Generator(client=mock_client)
    result = generator.generate("질문", MOCK_CHUNKS)
    assert isinstance(result, str)


def test_generator_empty_chunks_still_responds():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="관련 정보를 찾을 수 없습니다."))]
    mock_client.chat.completions.create.return_value = mock_response

    generator = Generator(client=mock_client)
    result = generator.generate("질문", [])
    assert isinstance(result, str)
