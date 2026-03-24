"""Medium Tech crawler.

Medium is a publishing platform where writers share stories and ideas, with a strong tech community.
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article

logger = logging.getLogger(__name__)


class MediumTechCrawler(BaseCrawler):
    """Crawler for Medium Tech - https://medium.com/tag/technology"""

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from Medium Tech.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        logger.warning("Medium is blocked by Cloudflare 403, skipping")
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
