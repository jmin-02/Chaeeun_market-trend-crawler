"""Danawa Tech (다나와) crawler.

Danawa Tech is a tech blog from Danawa, a Korean price comparison site.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class DanawaTechCrawler(BaseCrawler):
    """Crawler for Danawa Tech (다나와) - https://dpg.danawa.com/bbs/"""

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from Danawa Tech.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Danawa Tech news list items from /news/list page
        for item in soup.select(".list_item"):
            try:
                # Extract title from .post_title
                title_elem = item.select_one(".post_title")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                # Extract URL from a.info_link or first <a> with href
                link_elem = item.select_one("a.info_link") or item.select_one("a.thumb_link")
                if not link_elem:
                    continue
                url = link_elem.get("href", "")
                if not url:
                    continue
                if not url.startswith("http"):
                    url = f"https://dpg.danawa.com{url}"

                # Extract content preview from .post_desc or use title
                content_elem = item.select_one(".post_desc")
                content = content_elem.get_text(strip=True) if content_elem else title

                # Extract publication date
                time_elem = item.select_one(".date") or item.find("time")
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
