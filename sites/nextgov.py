"""Nextgov crawler.

Nextgov is the leading source of news and information for technology leaders in the public sector.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseCrawler
from .models import Article, Category, SourceLanguage
from .classification import classify_article


class NextgovCrawler(BaseCrawler):
    """Crawler for Nextgov - https://www.nextgov.com"""

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from Nextgov.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Nextgov article structure
        for item in soup.select("article") or soup.select(".article-item"):
            try:
                # Extract title
                title_elem = item.find("h2") or item.select_one(".title") or item.find("h3")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # Extract URL
                link_elem = item.find("a")
                if not link_elem:
                    continue
                url = link_elem.get("href", "")
                if url and not url.startswith("http"):
                    url = f"https://www.nextgov.com{url}"

                # Extract content preview
                content_elem = item.select_one(".excerpt") or item.select_one(".summary")
                content = content_elem.get_text(strip=True) if content_elem else title

                # Extract publication date
                time_elem = item.find("time")
                published_at = datetime.now()
                if time_elem:
                    datetime_str = time_elem.get("datetime") or time_elem.get_text(strip=True)
                    try:
                        published_at = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        pass

                # Extract author
                author_elem = item.select_one(".author") or item.select_one(".byline")
                author = author_elem.get_text(strip=True) if author_elem else None

                # Determine category from URL and title
                category = self._determine_category(url, title)

                article = Article(
                    title=title,
                    url=url,
                    content=content[:500],
                    source=source,
                    published_at=published_at,
                    author=author,
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
