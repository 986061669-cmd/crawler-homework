"""
parser.py - Douban movie data parser module.
Uses BeautifulSoup to extract structured data from HTML responses.
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class DoubanParser:
    """Parse Douban Top250 movie list pages."""

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "lxml")

    def parse_movie_list(self) -> List[Dict]:
        """
        Extract movie entries from a Top250 list page.

        Returns:
            List of dicts, each containing:
            - rank: ranking number
            - title: movie title (Chinese)
            - title_en: movie title (English/original)
            - info: director, actors, year, country, genre
            - rating: average rating score
            - rating_count: number of ratings
            - quote: memorable quote
            - detail_url: link to detail page
        """
        movies = []
        items = self.soup.select("ol.grid_view > li")

        for item in items:
            try:
                movie = self._parse_single_movie(item)
                if movie:
                    movies.append(movie)
            except Exception as e:
                print(f"  [Parser Warning] Failed to parse item: {e}")
                continue

        return movies

    def _parse_single_movie(self, item) -> Optional[Dict]:
        """Parse a single movie list item."""
        rank_el = item.select_one("em")
        title_el = item.select_one(".hd a span:first-child")
        title_other_el = item.select_one(".hd .other")
        info_el = item.select_one(".bd p:first-child")
        rating_el = item.select_one(".rating_num")
        rating_count_el = item.select_one(".bd .star span:last-child")
        quote_el = item.select_one(".inq")
        link_el = item.select_one(".hd a")

        if not title_el:
            return None

        # Extract info line: "director / actor / year / country / genre"
        info_text = info_el.get_text(strip=True) if info_el else ""
        parts = [p.strip() for p in info_text.split("\n") if p.strip()]
        info_line = parts[0] if parts else ""

        # Parse rating count: strip trailing text like "???"
        rating_count_text = ""
        if rating_count_el:
            rating_count_text = rating_count_el.get_text(strip=True)

        return {
            "rank": int(rank_el.get_text(strip=True)) if rank_el else None,
            "title": title_el.get_text(strip=True),
            "title_other": title_other_el.get_text(strip=True).lstrip(" / ").strip() if title_other_el else "",
            "info": info_line,
            "rating": float(rating_el.get_text(strip=True)) if rating_el else None,
            "rating_count": rating_count_text,
            "quote": quote_el.get_text(strip=True) if quote_el else "",
            "detail_url": link_el["href"] if link_el and link_el.has_attr("href") else "",
        }

    def get_next_page_url(self) -> Optional[str]:
        """Extract the next page URL from pagination."""
        next_link = self.soup.select_one("span.next a")
        if next_link and next_link.has_attr("href"):
            return next_link["href"]
        return None
