"""Kakao Tech (카카오 기술 블로그) crawler.

Kakao Tech is Kakao's engineering blog.
Uses RSS feed to avoid SPA rendering issues.
"""

import logging
from datetime import datetime

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..classification import classify_article
from ..models import Article, SourceLanguage

logger = logging.getLogger(__name__)


class KakaoTechCrawler(BaseCrawler):
    """Crawler for Kakao Tech - https://tech.kakao.com"""

    BASE_URL = "https://tech.kakao.com/feed"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from Kakao Tech RSS feed.

        Args:
            html: RSS XML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "xml")
        articles = []

        items = soup.find_all("item")
        logger.debug(f"Found {len(items)} items in RSS feed")

        for idx, item in enumerate(items):
            try:
                title_tag = item.find("title")
                link_tag = item.find("link")
                desc_tag = item.find("description")
                date_tag = item.find("pubDate")
                creator_tag = item.find("dc:creator") or item.find("creator")

                title = title_tag.get_text(strip=True) if title_tag else None
                url = link_tag.get_text(strip=True) if link_tag else None

                if not title or not url:
                    continue

                content = desc_tag.get_text(strip=True) if desc_tag else title
                author = creator_tag.get_text(strip=True) if creator_tag else None

                published_at = datetime.now()
                if date_tag:
                    try:
                        published_at = datetime.strptime(
                            date_tag.get_text(strip=True), "%a, %d %b %Y %H:%M:%S %z"
                        )
                    except ValueError:
                        pass

                category = classify_article(url, title)

                article = Article(
                    title=title,
                    url=url,
                    content=content[:500],
                    source=source,
                    published_at=published_at,
                    category=category,
                    author=author,
                    language=SourceLanguage.KOREAN if language == "ko" else SourceLanguage.ENGLISH,
                )

                articles.append(article)
                logger.debug(f"Successfully extracted article {idx}: {title[:50]}...")

            except Exception as e:
                logger.warning(f"Failed to extract article {idx}: {e}")
                continue

        logger.info(f"Successfully extracted {len(articles)} articles from {source}")
        return articles
