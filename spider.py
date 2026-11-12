"""
spider.py - Douban Top250 Spider.
Main controller that orchestrates requests, parsing, and storage.
Implements anti-crawl strategies: random User-Agent, delays, retries.
"""

import time
import random
import requests
from typing import List, Dict

from parser import DoubanParser
from storage import CSVStorage


class DoubanSpider:
    """
    A polite web spider for Douban Top250 movie list.

    Anti-crawl strategies:
    - Rotating User-Agent headers (via fake-useragent or built-in pool)
    - Random delay between requests (1-3 seconds)
    - Automatic retry on failure (up to 3 attempts)
    - Referer header spoofing
    """

    BASE_URL = "https://movie.douban.com/top250"

    # Built-in User-Agent pool (fallback if fake-useragent unavailable)
    UA_POOL = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, delay_range: tuple = (1.0, 3.0), max_retries: int = 3):
        """
        Args:
            delay_range: (min, max) seconds to wait between requests
            max_retries: max retry attempts per request
        """
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.session = requests.Session()
        self.storage = CSVStorage()
        self.all_movies: List[Dict] = []

    def _get_headers(self) -> dict:
        """Generate randomized request headers."""
        try:
            from fake_useragent import UserAgent
            ua = UserAgent().random
        except Exception:
            ua = random.choice(self.UA_POOL)

        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://movie.douban.com/",
            "Connection": "keep-alive",
        }

    def _request(self, url: str) -> str:
        """
        Make an HTTP GET request with retry logic.

        Args:
            url: target URL

        Returns:
            Response HTML text.

        Raises:
            requests.RequestException: if all retries fail.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"  [Request] GET {url} (attempt {attempt}/{self.max_retries})")
                resp = self.session.get(url, headers=self._get_headers(), timeout=15)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException as e:
                print(f"  [Error] {e}")
                if attempt < self.max_retries:
                    wait = attempt * 2
                    print(f"  [Retry] Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise

    def _polite_delay(self):
        """Random delay between requests to avoid detection."""
        delay = random.uniform(*self.delay_range)
        print(f"  [Delay] Sleeping {delay:.1f}s...")
        time.sleep(delay)

    def crawl(self, max_pages: int = 10) -> List[Dict]:
        """
        Crawl Douban Top250 movie list.

        Args:
            max_pages: max number of pages to crawl (default 10 = all 250 movies)

        Returns:
            List of all parsed movie dicts.
        """
        print("=" * 60)
        print("  Douban Top250 Spider - Starting")
        print("=" * 60)

        url = self.BASE_URL
        page = 0

        while url and page < max_pages:
            page += 1
            print(f"\n[Page {page}] Crawling: {url}")

            try:
                html = self._request(url)
            except requests.RequestException as e:
                print(f"[Fatal] Failed to fetch page {page}: {e}")
                break

            parser = DoubanParser(html)
            movies = parser.parse_movie_list()

            if not movies:
                print(f"  [Warning] No movies found on page {page}, stopping.")
                break

            self.all_movies.extend(movies)
            print(f"  [Parsed] {len(movies)} movies (total: {len(self.all_movies)})")

            # Get next page URL
            next_url = parser.get_next_page_url()
            if next_url:
                url = next_url if next_url.startswith("http") else f"https://movie.douban.com{next_url}"
            else:
                url = None

            # Polite delay before next request
            if url:
                self._polite_delay()

        print(f"\n{'=' * 60}")
        print(f"  Crawling complete! Total movies: {len(self.all_movies)}")
        print(f"{'=' * 60}")

        return self.all_movies

    def save_results(self, filename: str = None) -> str:
        """Save all collected movies to CSV."""
        return self.storage.save(self.all_movies, filename)


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    spider = DoubanSpider(delay_range=(1.5, 3.0), max_retries=3)
    movies = spider.crawl(max_pages=10)

    if movies:
        filepath = spider.save_results()
        print(f"\n[Done] Results saved to: {filepath}")
    else:
        print("\n[Done] No data collected.")
