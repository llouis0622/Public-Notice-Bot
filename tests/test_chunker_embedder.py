import pytest
from unittest.mock import patch, MagicMock

from src.pipeline.chunker import chunk_posting
from src.pipeline.embedder import BaseEmbedder, OpenAIEmbedder, embed_chunks


NORMALIZED = {
    "source": "busan_gov",
    "url": "https://www.busan.go.kr/noticeView?ntcId=AAA001",
    "title": "2024년 부산청년 장학금 모집",
    "organization": "부산광역시",
    "eligibility_text": "부산 거주 대학생",
    "benefits_text": "학비 최대 200만원 지원",
    "apply_method_text": "온라인 접수",
    "requirements_text": None,
    "deadline_at": None,
    "raw_content": "지원자격: 부산 거주 대학생\n지원내용: 학비 최대 200만원 지원\n신청방법: 온라인 접수",
}

NORMALIZED_MINIMAL = {
    "source": "busan_gov",
    "url": "https://www.busan.go.kr/noticeView?ntcId=BBB001",
    "title": "간단 공고",
    "organization": None,
    "eligibility_text": None,
    "benefits_text": None,
    "apply_method_text": None,
    "requirements_text": None,
    "deadline_at": None,
    "raw_content": "공고 내용입니다.",
}


def test_chunk_posting_returns_list():
    chunks = chunk_posting(NORMALIZED)
    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_each_chunk_has_required_keys():
    chunks = chunk_posting(NORMALIZED)
    for chunk in chunks:
        assert "chunk_type" in chunk
        assert "content" in chunk
        assert "source_span_start" in chunk
        assert "source_span_end" in chunk


def test_chunk_types_are_valid():
    from src.db.models import CHUNK_TYPES
    chunks = chunk_posting(NORMALIZED)
    for chunk in chunks:
        assert chunk["chunk_type"] in CHUNK_TYPES


def test_eligibility_chunk_created():
    chunks = chunk_posting(NORMALIZED)
    types = [c["chunk_type"] for c in chunks]
    assert "지원자격" in types


def test_benefits_chunk_created():
    chunks = chunk_posting(NORMALIZED)
    types = [c["chunk_type"] for c in chunks]
    assert "혜택" in types


def test_apply_method_chunk_created():
    chunks = chunk_posting(NORMALIZED)
    types = [c["chunk_type"] for c in chunks]
    assert "신청방법" in types


def test_none_fields_skipped():
    chunks = chunk_posting(NORMALIZED)
    for chunk in chunks:
        assert chunk["content"]


def test_minimal_posting_gets_기타_chunk():
    chunks = chunk_posting(NORMALIZED_MINIMAL)
    types = [c["chunk_type"] for c in chunks]
    assert "기타" in types


def test_source_span_end_greater_than_start():
    chunks = chunk_posting(NORMALIZED)
    for chunk in chunks:
        if chunk["source_span_start"] is not None:
            assert chunk["source_span_end"] >= chunk["source_span_start"]


def test_base_embedder_is_abstract():
    with pytest.raises(TypeError):
        BaseEmbedder()


def test_openai_embedder_is_subclass():
    assert issubclass(OpenAIEmbedder, BaseEmbedder)


def test_openai_embedder_calls_api():
    mock_vector = [0.1] * 1536
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=mock_vector)]

    embedder = OpenAIEmbedder(api_key="test-key")
    with patch.object(embedder.client.embeddings, "create", return_value=mock_response):
        result = embedder.embed("테스트 텍스트")
    assert result == mock_vector


def test_openai_embedder_returns_list_of_floats():
    mock_vector = [0.1] * 1536
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=mock_vector)]

    embedder = OpenAIEmbedder(api_key="test-key")
    with patch.object(embedder.client.embeddings, "create", return_value=mock_response):
        result = embedder.embed("테스트")
    assert isinstance(result, list)
    assert len(result) == 1536


def test_embed_chunks_attaches_embedding():
    mock_vector = [0.1] * 1536
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = mock_vector

    chunks = chunk_posting(NORMALIZED)
    embed_chunks(chunks, mock_embedder)
    for chunk in chunks:
        assert "embedding" in chunk
        assert chunk["embedding"] == mock_vector


def test_embed_chunks_calls_embed_per_chunk():
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = [0.0] * 1536

    chunks = chunk_posting(NORMALIZED)
    embed_chunks(chunks, mock_embedder)
    assert mock_embedder.embed.call_count == len(chunks)
