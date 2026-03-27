from abc import ABC, abstractmethod
import time
import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse


class BaseCrawler(ABC):
    delay = 1.0
    max_retries = 3
    timeout = 10

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PublicNoticeBot/1.0 (+https://github.com/public-notice-bot)"
        })
        self._robot_parsers = {}

    def _check_robots(self, url):
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
            except Exception:
                return True
            self._robot_parsers[base] = rp
        return self._robot_parsers[base].can_fetch(self.session.headers["User-Agent"], url)

    def _get(self, url):
        last_exc = None
        for attempt in range(self.max_retries):
            if attempt > 0:
                time.sleep(self.delay * (2 ** (attempt - 1)))
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                last_exc = e
        raise last_exc

    @abstractmethod
    def fetch_list(self, page=1):
        pass

    @abstractmethod
    def fetch_detail(self, url):
        pass

    @abstractmethod
    def parse_list(self, html):
        pass

    @abstractmethod
    def parse_detail(self, html):
        pass
