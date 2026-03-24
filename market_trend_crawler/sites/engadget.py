"""Engadget crawler.

Engadget is a multilingual technology blog network with daily coverage of gadgets and consumer electronics.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class EngadgetCrawler(BaseCrawler):
    """Crawler for Engadget - https://www.engadget.com"""

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from Engadget.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Engadget uses h4 a tags inside stream containers
        seen_urls = set()

        # Try stream container first, fall back to all h4 a tags
        stream = soup.select_one('[data-test="stream"]')
        if stream:
            link_elems = stream.select("h4 a")
        else:
            link_elems = soup.select("h4 a")

        for link_elem in link_elems:
            try:
                url = link_elem.get("href", "")
                if not url:
                    continue

                # Resolve relative URLs
                if not url.startswith("http"):
                    url = f"https://www.engadget.com{url}"

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
