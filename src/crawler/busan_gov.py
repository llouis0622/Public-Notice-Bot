import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.crawler.base import BaseCrawler


BASE_URL = "https://www.busan.go.kr"
LIST_URL = "https://www.busan.go.kr/news/notice"


class BusanGovCrawler(BaseCrawler):
    delay = 1.5
    source = "busan_gov"

    def fetch_list(self, page=1):
        params_url = f"{LIST_URL}?pageIndex={page}"
        if not self._check_robots(params_url):
            return []
        time.sleep(self.delay)
        resp = self._get(params_url)
        return self.parse_list(resp.text)

    def fetch_detail(self, url):
        if not self._check_robots(url):
            return None
        time.sleep(self.delay)
        resp = self._get(url)
        return resp.text

    def parse_list(self, html):
        soup = BeautifulSoup(html, "lxml")
        urls = []
        for a in soup.select(".board-list a[href]"):
            href = a["href"]
            full_url = urljoin(BASE_URL, href)
            urls.append(full_url)
        return urls

    def parse_detail(self, html):
        soup = BeautifulSoup(html, "lxml")

        title_tag = (
            soup.select_one(".view-title h3")
            or soup.select_one(".view-title h2")
            or soup.select_one(".bbs-view-title")
            or soup.select_one("h3.title")
        )
        title = title_tag.get_text(strip=True) if title_tag else ""

        content_tag = soup.select_one(".view-content") or soup.select_one(".bbs-view-content")
        content_text = content_tag.get_text(separator="\n", strip=True) if content_tag else ""

        organization = self._extract_between(content_text, ["주관기관:", "담당부서:", "주관:"])
        deadline_at = self._extract_date(content_text, ["신청기간:", "접수기간:", "마감일:"])

        return {
            "source": self.source,
            "title": title,
            "organization": organization,
            "deadline_at": deadline_at,
            "raw_content": content_text,
        }

    def _extract_between(self, text, labels):
        for label in labels:
            idx = text.find(label)
            if idx == -1:
                continue
            start = idx + len(label)
            end = text.find("\n", start)
            value = text[start:end].strip() if end != -1 else text[start:].strip()
            if value:
                return value
        return None

    def _extract_date(self, text, labels):
        import re
        for label in labels:
            idx = text.find(label)
            if idx == -1:
                continue
            snippet = text[idx:idx + 60]
            match = re.search(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}", snippet)
            if match:
                return match.group()
        return None
