"""Hankyung Tech (한국경제) crawler.

Hankyung Tech is the tech section of Korea Economic Daily.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class HankyungTechCrawler(BaseCrawler):
    """Crawler for Hankyung Tech (한국경제) - https://www.hankyung.com"""

    BASE_URL = "https://www.hankyung.com"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from Hankyung Tech.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Hankyung Tech article list items
        for item in soup.select("div.news-item"):
            try:
                # Extract title
                title_elem = item.select_one("h2.news-tit a")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # Extract URL
                link_elem = item.select_one("h2.news-tit a")
                if not link_elem:
                    continue
                url = link_elem.get("href", "")
                if url and not url.startswith("http"):
                    url = f"https://www.hankyung.com{url}"

                # Extract content preview
                content_elem = item.select_one("p.news-subtit")
                content = content_elem.get_text(strip=True) if content_elem else title

                # Extract publication date
                time_elem = item.select_one("p.txt-date")
                published_at = datetime.now()
                if time_elem:
                    datetime_str = time_elem.get_text(strip=True)
                    try:
                        published_at = datetime.strptime(datetime_str, "%Y.%m.%d %H:%M")
                    except ValueError:
                        try:
                            published_at = datetime.strptime(datetime_str, "%Y.%m.%d")
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
