import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.crawler.base import BaseCrawler


BASE_URL = "https://youth.busan.go.kr"
LIST_URL = "https://youth.busan.go.kr/youth/program/list"


class BusanYouthCrawler(BaseCrawler):
    delay = 1.5
    source = "busan_youth"

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
            soup.select_one(".view-title")
            or soup.select_one("h2.view-title")
            or soup.select_one("h3.view-title")
        )
        title = title_tag.get_text(strip=True) if title_tag else ""

        table_data = {}
        for row in soup.select(".view-body table tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td:
                table_data[th.get_text(strip=True)] = td.get_text(strip=True)

        organization = (
            table_data.get("주관기관")
            or table_data.get("주최기관")
            or table_data.get("담당부서")
        )
        deadline_at = self._extract_date_from_range(
            table_data.get("신청기간") or table_data.get("접수기간") or ""
        )

        return {
            "source": self.source,
            "title": title,
            "organization": organization,
            "deadline_at": deadline_at,
            "raw_content": "\n".join(f"{k}: {v}" for k, v in table_data.items()),
        }

    def _extract_date_from_range(self, text):
        import re
        matches = re.findall(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}", text)
        if len(matches) >= 2:
            return matches[1]
        if matches:
            return matches[0]
        return None
