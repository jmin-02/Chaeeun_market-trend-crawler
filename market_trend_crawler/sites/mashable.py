"""Mashable crawler.

Mashable is a global digital media and entertainment company.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class MashableCrawler(BaseCrawler):
    """Crawler for Mashable - https://mashable.com"""

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from Mashable.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Mashable uses links with /article/ prefix
        seen_urls = set()

        for link_elem in soup.select('a[href^="/article/"]'):
            try:
                url = link_elem.get("href", "")
                if not url:
                    continue

                # Prepend base URL for relative paths
                url = f"https://mashable.com{url}"

                # Deduplicate
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title = link_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                content = title
                published_at = datetime.now()

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
