import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from src.crawler.base import BaseCrawler
from src.crawler.busan_gov import BusanGovCrawler


LIST_HTML = """
<html><body>
  <div class="board-list">
    <ul>
      <li><a href="/noticeView?ntcId=AAA001">장학금 모집 공고</a></li>
      <li><a href="/noticeView?ntcId=AAA002">청년 취업 지원 사업</a></li>
    </ul>
  </div>
</body></html>
"""

DETAIL_HTML = """
<html><body>
  <div class="view-title">
    <h3>2024년 부산청년 장학금 모집</h3>
  </div>
  <div class="view-content">
    <p>신청기간: 2024-03-01 ~ 2024-03-31</p>
    <p>지원자격: 부산 거주 대학생</p>
    <p>지원내용: 학비 최대 200만원 지원</p>
    <p>신청방법: 온라인 접수</p>
    <p>주관기관: 부산광역시</p>
  </div>
</body></html>
"""


def test_busan_gov_crawler_is_subclass_of_base():
    assert issubclass(BusanGovCrawler, BaseCrawler)


def test_base_crawler_is_abstract():
    with pytest.raises(TypeError):
        BaseCrawler()


def test_parse_list_returns_urls():
    crawler = BusanGovCrawler()
    urls = crawler.parse_list(LIST_HTML)
    assert len(urls) == 2
    assert all(u.startswith("https://www.busan.go.kr") for u in urls)


def test_parse_detail_returns_required_fields():
    crawler = BusanGovCrawler()
    result = crawler.parse_detail(DETAIL_HTML)
    assert result["title"]
    assert result["source"] == "busan_gov"


def test_parse_detail_extracts_title():
    crawler = BusanGovCrawler()
    result = crawler.parse_detail(DETAIL_HTML)
    assert "장학금" in result["title"]


def test_parse_detail_extracts_organization():
    crawler = BusanGovCrawler()
    result = crawler.parse_detail(DETAIL_HTML)
    assert result.get("organization") is not None


def test_fetch_list_calls_get_with_correct_url():
    crawler = BusanGovCrawler()
    mock_resp = MagicMock()
    mock_resp.text = LIST_HTML
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp) as mock_get:
        with patch.object(crawler, "_check_robots", return_value=True):
            result = crawler.fetch_list(page=1)
    assert mock_get.called
    assert isinstance(result, list)


def test_fetch_detail_calls_get_with_url():
    crawler = BusanGovCrawler()
    url = "https://www.busan.go.kr/noticeView?ntcId=AAA001"
    mock_resp = MagicMock()
    mock_resp.text = DETAIL_HTML
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp) as mock_get:
        with patch.object(crawler, "_check_robots", return_value=True):
            result = crawler.fetch_detail(url)
    mock_get.assert_called_once_with(url, timeout=crawler.timeout)
    assert result == DETAIL_HTML


def test_retry_on_request_exception():
    import requests
    crawler = BusanGovCrawler()
    crawler.delay = 0

    call_count = {"n": 0}

    def flaky_get(url, **kwargs):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise requests.RequestException("timeout")
        mock_resp = MagicMock()
        mock_resp.text = DETAIL_HTML
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    with patch.object(crawler.session, "get", side_effect=flaky_get):
        with patch.object(crawler, "_check_robots", return_value=True):
            result = crawler._get("https://www.busan.go.kr/noticeView?ntcId=AAA001")
    assert call_count["n"] == 3
    assert result.text == DETAIL_HTML


def test_get_raises_after_max_retries():
    import requests
    crawler = BusanGovCrawler()
    crawler.delay = 0

    with patch.object(crawler.session, "get", side_effect=requests.RequestException("fail")):
        with patch.object(crawler, "_check_robots", return_value=True):
            with pytest.raises(requests.RequestException):
                crawler._get("https://www.busan.go.kr/noticeView?ntcId=AAA001")
