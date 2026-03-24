"""CIO Korea (아이오티) crawler.

CIO Korea is a Korean IT media site for CIOs and IT professionals.
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article

logger = logging.getLogger(__name__)


class CIOKoreaCrawler(BaseCrawler):
    """Crawler for CIO Korea (아이오티) - https://www.ciokorea.com"""

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from CIO Korea.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        logger.warning("CIO Korea redirects to Japan CIO, not Korean content, skipping")
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
