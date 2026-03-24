"""Naver Tech (D2) crawler.

Naver Tech is Naver's developer and tech blog.
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article

logger = logging.getLogger(__name__)


class NaverTechCrawler(BaseCrawler):
    """Crawler for Naver Tech (D2) - https://d2.naver.com"""

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from Naver Tech.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        logger.warning("Naver D2 requires JavaScript rendering, skipping")
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
