"""Hacker News (Y Combinator) crawler.

Hacker News is a social news website focusing on computer science and entrepreneurship.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class HackerNewsCrawler(BaseCrawler):
    """Crawler for Hacker News - https://news.ycombinator.com"""

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from Hacker News.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Hacker News uses table-based layout: each story is a <tr class="athing">
        rows = soup.select("tr.athing")
        for i, row in enumerate(rows):
            try:
                # Title and URL are inside .titleline > a within the athing row
                title_elem = row.select_one(".titleline > a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                url = title_elem.get("href", "")

                if not title or not url:
                    continue

                # Resolve relative URLs (e.g., item?id=... links)
                if not url.startswith("http"):
                    url = f"https://news.ycombinator.com/{url}"

                # Hacker News doesn't have content previews
                content = title
                published_at = datetime.now()

                # Determine category from URL and title
                category = self._determine_category(url, title)

                article = Article(
                    title=title,
                    url=url,
                    content=content[:500],
                    source=source,
                    published_at=published_at,
                    category=category,
                    language=SourceLanguage.ENGLISH,
                )
                articles.append(article)

            except Exception as e:
                continue

        return articles

    def _determine_category(self, url: str, title: str) -> Category:
        """Determine category from URL and title using centralized classification.

        Args:
            url: Article URL
            title: Article title

        Returns:
            Category enum value
        """
        return classify_article(url, title)
