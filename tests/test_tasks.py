import pytest
from unittest.mock import patch, MagicMock

from src.tasks.crawler_tasks import crawl_source, crawl_all


def test_crawl_source_busan_gov_calls_crawler():
    mock_crawler = MagicMock()
    mock_crawler.fetch_list.return_value = ["https://www.busan.go.kr/noticeView?ntcId=AAA001"]
    mock_crawler.fetch_detail.return_value = "<html>detail</html>"
    mock_crawler.parse_detail.return_value = {
        "source": "busan_gov",
        "url": "https://www.busan.go.kr/noticeView?ntcId=AAA001",
        "title": "장학금 모집",
        "raw_content": "내용",
    }

    with patch("src.tasks.crawler_tasks.BusanGovCrawler", return_value=mock_crawler):
        with patch("src.tasks.crawler_tasks.run_pipeline", return_value={"saved": 1, "skipped": 0}) as mock_pipeline:
            result = crawl_source("busan_gov")

    assert result["source"] == "busan_gov"
    assert mock_pipeline.called


def test_crawl_source_busan_youth_calls_crawler():
    mock_crawler = MagicMock()
    mock_crawler.fetch_list.return_value = []

    with patch("src.tasks.crawler_tasks.BusanYouthCrawler", return_value=mock_crawler):
        with patch("src.tasks.crawler_tasks.run_pipeline", return_value={"saved": 0, "skipped": 0}):
            result = crawl_source("busan_youth")

    assert result["source"] == "busan_youth"


def test_crawl_source_unknown_raises():
    with pytest.raises(ValueError):
        crawl_source("unknown_source")


def test_crawl_all_runs_all_sources():
    with patch("src.tasks.crawler_tasks.crawl_source") as mock_crawl:
        mock_crawl.return_value = {"source": "x", "saved": 0, "skipped": 0}
        results = crawl_all()
    assert len(results) == 2
    called_sources = {c.args[0] for c in mock_crawl.call_args_list}
    assert "busan_gov" in called_sources
    assert "busan_youth" in called_sources


def test_run_pipeline_saves_new_posting():
    from src.tasks.crawler_tasks import run_pipeline

    raw = {
        "source": "busan_gov",
        "url": "https://www.busan.go.kr/noticeView?ntcId=NEW001",
        "title": "신규 공고",
        "raw_content": "지원자격: 부산 거주자\n지원내용: 100만원",
    }

    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    with patch("src.tasks.crawler_tasks.get_db_session") as mock_ctx:
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        with patch("src.tasks.crawler_tasks.embed_chunks"):
            with patch("src.tasks.crawler_tasks.OpenAIEmbedder"):
                result = run_pipeline([raw])

    assert result["saved"] == 1
    assert result["skipped"] == 0


def test_run_pipeline_skips_duplicate():
    from src.tasks.crawler_tasks import run_pipeline

    raw = {
        "source": "busan_gov",
        "url": "https://www.busan.go.kr/noticeView?ntcId=DUP001",
        "title": "중복 공고",
        "raw_content": "동일 내용",
    }

    mock_posting = MagicMock()
    mock_posting.raw_hash = __import__("hashlib").sha256("동일 내용".encode()).hexdigest()

    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_posting

    with patch("src.tasks.crawler_tasks.get_db_session") as mock_ctx:
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        with patch("src.tasks.crawler_tasks.embed_chunks"):
            with patch("src.tasks.crawler_tasks.OpenAIEmbedder"):
                result = run_pipeline([raw])

    assert result["skipped"] == 1
    assert result["saved"] == 0
