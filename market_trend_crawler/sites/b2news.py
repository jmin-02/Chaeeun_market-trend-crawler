"""B2News (비투뉴스) crawler.

B2News is a Korean B2B tech news site.
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article

logger = logging.getLogger(__name__)


class B2NewsCrawler(BaseCrawler):
    """Crawler for B2News (비투뉴스) - https://www.b2news.co.kr"""

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from B2News.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        logger.warning("B2News DNS is dead, site closed, skipping")
        return []

    def _determine_category(self, url: str, title: str) -> Category:
        """Determine category from URL and title using centralized classification.

        Args:
            url: Article URL
            title: Article title

        Returns:
            Category enum value
        """
        return classify_article(url, title)
