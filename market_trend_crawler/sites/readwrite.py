"""ReadWrite crawler.

ReadWrite is a leading publication for the developer community covering technology and innovation.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class ReadWriteCrawler(BaseCrawler):
    """Crawler for ReadWrite - https://readwrite.com"""

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from ReadWrite.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # ReadWrite uses h2/h3 links for article headlines
        seen_urls = set()

        for link_elem in soup.select("h2 a[href]") + soup.select("h3 a[href]"):
            try:
                url = link_elem.get("href", "")
                if not url:
                    continue

                # Resolve relative URLs
                if not url.startswith("http"):
                    url = f"https://readwrite.com{url}"

                # Deduplicate
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title = link_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                content = title
                published_at = datetime.now()

                # Try to find a time element nearby
                parent = link_elem.find_parent("article") or link_elem.find_parent()
                if parent:
                    time_elem = parent.find("time")
                    if time_elem:
                        datetime_str = time_elem.get("datetime", "")
                        if datetime_str:
                            try:
                                published_at = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass

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
