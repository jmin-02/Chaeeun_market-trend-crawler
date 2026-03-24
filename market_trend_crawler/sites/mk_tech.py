"""MK Tech (매일경제) crawler.

MK Tech is the tech section of MK Business.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class MKTechCrawler(BaseCrawler):
    """Crawler for MK Tech (매일경제) - https://www.mk.co.kr"""

    BASE_URL = "https://www.mk.co.kr"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from MK Tech.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # MK Tech article list items (each item is an <a> tag)
        for item in soup.select("a.news_item"):
            try:
                # Extract title
                title_elem = item.select_one("h4")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # Extract URL (the <a> tag itself has the href)
                url = item.get("href", "")
                if not url:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.mk.co.kr{url}"

                # Extract content preview
                content_elem = item.select_one("p.art_desc")
                content = content_elem.get_text(strip=True) if content_elem else title

                # Extract publication date
                time_elem = item.select_one("p.time_info")
                published_at = datetime.now()
                if time_elem:
                    datetime_str = time_elem.get_text(strip=True)
                    try:
                        published_at = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        try:
                            published_at = datetime.strptime(datetime_str, "%Y-%m-%d")
                        except ValueError:
                            pass

                # Determine category
                category = self._determine_category(url, title)

                article = Article(
                    title=title,
                    url=url,
                    content=content[:500],
                    source=source,
                    published_at=published_at,
                    category=category,
                    language=SourceLanguage.KOREAN,
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
