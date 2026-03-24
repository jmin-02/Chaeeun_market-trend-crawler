"""Hacker News (Y Combinator) crawler.

Hacker News is a social news website focusing on computer science and entrepreneurship.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseCrawler
from .models import Article, Category, SourceLanguage
from .classification import classify_article


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

        # Hacker News uses a specific table structure
        rows = soup.select("tr.athing")
        for i, row in enumerate(rows):
            try:
                # Extract title and URL from the next row
                title_row = row.find_next_sibling("tr")
                if not title_row:
                    continue

                title_elem = title_row.find("a", class_="storylink")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                url = title_elem.get("href", "")

                # Extract subtext row for date and other info
                subtext_row = title_row.find_next_sibling("tr")
                if subtext_row:
                    subtext = subtext_row.get_text(strip=True)

                    # Extract date
                    published_at = datetime.now()
                    if "ago" in subtext:
                        # Parse "X hours ago" format
                        import re
                        hours_match = re.search(r'(\d+)\s+hours?\s+ago', subtext)
                        if hours_match:
                            hours = int(hours_match.group(1))
                            published_at = datetime.now() - datetime.timedelta(hours=hours)

                # Hacker News doesn't always have content previews
                content = title

                # Determine category from URL and title
                category = self._determine_category(url, title)

                article = Article(
                    title=title,
                    url=url,
                    content=content[:500],
                    source=source,
                    published_at=published_at,
                    author=None,  # Hacker News usernames aren't always displayed in list view
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
