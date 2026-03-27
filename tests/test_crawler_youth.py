import pytest
from unittest.mock import patch, MagicMock

from src.crawler.base import BaseCrawler
from src.crawler.busan_youth import BusanYouthCrawler


LIST_HTML = """
<html><body>
  <div class="list-wrap">
    <ul class="board-list">
      <li>
        <a href="/youth/program/view?seq=101">청년 창업 지원 프로그램</a>
        <span class="date">2024-03-31</span>
      </li>
      <li>
        <a href="/youth/program/view?seq=102">부산 청년 주거 지원</a>
        <span class="date">2024-04-15</span>
      </li>
    </ul>
  </div>
</body></html>
"""

DETAIL_HTML = """
<html><body>
  <div class="view-wrap">
    <h2 class="view-title">2024 청년 창업 지원 프로그램 모집</h2>
    <div class="view-body">
      <table>
        <tr><th>주관기관</th><td>부산광역시 청년정책과</td></tr>
        <tr><th>신청기간</th><td>2024-03-01 ~ 2024-03-31</td></tr>
        <tr><th>지원자격</th><td>부산 거주 만 19~39세 청년</td></tr>
        <tr><th>지원내용</th><td>창업 초기 자금 최대 1000만원</td></tr>
        <tr><th>신청방법</th><td>온라인 접수 (부산청년플랫폼 홈페이지)</td></tr>
      </table>
    </div>
  </div>
</body></html>
"""


def test_busan_youth_crawler_is_subclass_of_base():
    assert issubclass(BusanYouthCrawler, BaseCrawler)


def test_parse_list_returns_urls():
    crawler = BusanYouthCrawler()
    urls = crawler.parse_list(LIST_HTML)
    assert len(urls) == 2
    assert all(u.startswith("https://youth.busan.go.kr") for u in urls)


def test_parse_detail_returns_required_fields():
    crawler = BusanYouthCrawler()
    result = crawler.parse_detail(DETAIL_HTML)
    assert result["title"]
    assert result["source"] == "busan_youth"


def test_parse_detail_extracts_title():
    crawler = BusanYouthCrawler()
    result = crawler.parse_detail(DETAIL_HTML)
    assert "청년" in result["title"]


def test_parse_detail_extracts_organization():
    crawler = BusanYouthCrawler()
    result = crawler.parse_detail(DETAIL_HTML)
    assert result.get("organization") is not None
    assert "부산" in result["organization"]


def test_parse_detail_extracts_deadline():
    crawler = BusanYouthCrawler()
    result = crawler.parse_detail(DETAIL_HTML)
    assert result.get("deadline_at") is not None
    assert "2024" in result["deadline_at"]


def test_fetch_list_calls_get_with_correct_url():
    crawler = BusanYouthCrawler()
    mock_resp = MagicMock()
    mock_resp.text = LIST_HTML
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp) as mock_get:
        with patch.object(crawler, "_check_robots", return_value=True):
            result = crawler.fetch_list(page=1)
    assert mock_get.called
    assert isinstance(result, list)


def test_fetch_detail_returns_html():
    crawler = BusanYouthCrawler()
    url = "https://youth.busan.go.kr/youth/program/view?seq=101"
    mock_resp = MagicMock()
    mock_resp.text = DETAIL_HTML
    mock_resp.raise_for_status = MagicMock()

    with patch.object(crawler.session, "get", return_value=mock_resp):
        with patch.object(crawler, "_check_robots", return_value=True):
            result = crawler.fetch_detail(url)
    assert result == DETAIL_HTML
