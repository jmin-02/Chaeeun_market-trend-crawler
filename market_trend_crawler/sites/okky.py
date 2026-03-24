"""OKKY crawler.

OKKY is a Korean developer community and tech blog platform.
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article

logger = logging.getLogger(__name__)


class OKKYCrawler(BaseCrawler):
    """Crawler for OKKY - https://okky.kr"""

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from OKKY.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        logger.warning("OKKY requires JavaScript rendering, skipping")
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
