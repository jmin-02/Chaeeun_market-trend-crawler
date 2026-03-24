"""ITWorld Korea crawler.

ITWorld Korea is a Korean IT news site for enterprise and technology professionals.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class ITWorldKoreaCrawler(BaseCrawler):
    """Crawler for ITWorld Korea - https://www.itworld.co.kr"""

    BASE_URL = "https://www.itworld.co.kr"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from ITWorld Korea.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # ITWorld Korea article list items (each card is an <a> tag)
        for item in soup.select("a.card"):
            try:
                # Extract title
                title_elem = item.select_one("h3")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # Extract URL (the <a> tag itself has the href)
                url = item.get("href", "")
                if not url:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.itworld.co.kr{url}"

                # Extract content preview
                content_elem = item.select_one(".excerpt") or item.select_one(".summary")
                content = content_elem.get_text(strip=True) if content_elem else title

                # Extract publication date
                time_elem = item.find("time") or item.select_one(".date")
                published_at = datetime.now()
                if time_elem:
                    datetime_str = time_elem.get("datetime") or time_elem.get_text(strip=True)
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
