"""TechRadar crawler.

TechRadar is the source for tech buying advice, news and reviews.
NOTE: Disabled due to 403 blocking. Site config has enabled=False.
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article

logger = logging.getLogger(__name__)


class TechRadarCrawler(BaseCrawler):
    """Crawler for TechRadar - https://www.techradar.com

    NOTE: TechRadar returns 403 for automated requests. This crawler is disabled.
    """

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from TechRadar.

        Currently disabled due to 403 blocking by TechRadar.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            Empty list (site is blocked)
        """
        logger.warning(
            "TechRadar crawler is disabled: site returns 403 for automated requests. "
            "Returning empty list."
        )
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
