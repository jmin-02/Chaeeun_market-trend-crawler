"""Woowahan (우아한형제들) tech blog crawler.

Woowahan Bros (Baemin) engineering blog covering backend, frontend, and infrastructure.
"""

import logging
import re
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..classification import classify_article
from ..error_handling import (
    ErrorType,
    ExtractionError,
    create_error_context,
    handle_exception,
)
from ..models import Article, Category, SourceLanguage

logger = logging.getLogger(__name__)


class WoowahanCrawler(BaseCrawler):
    """Crawler for Woowahan Tech Blog - https://techblog.woowahan.com"""

    BASE_URL = "https://techblog.woowahan.com"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from Woowahan tech blog.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Find all links matching the woowahan blog post URL pattern
        url_pattern = re.compile(r"https://techblog\.woowahan\.com/\d+/?")
        link_elements = soup.find_all("a", href=url_pattern)

        logger.debug(f"Found {len(link_elements)} article links to process")

        seen_urls = set()
        idx = 0
        for link in link_elements:
            try:
                url = link.get("href", "").strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                title = link.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                content = title
                category = classify_article(url, title)

                article = Article(
                    title=title,
                    url=url,
                    content=content,
                    source=source,
                    published_at=datetime.now(),
                    category=category,
                    language=SourceLanguage.KOREAN if language == "ko" else SourceLanguage.ENGLISH,
                )

                articles.append(article)
                logger.debug(f"Successfully extracted article {idx}: {title[:50]}...")
                idx += 1

            except Exception as e:
                error_context = create_error_context(
                    source=source,
                    article_index=idx,
                    additional_info={"language": language},
                )
                extraction_error = handle_exception(
                    e, error_context, default_error_type=ErrorType.EXTRACTION
                )
                logger.warning(f"Failed to extract article {idx}: {extraction_error.message}")
                if self.config.log_extraction_errors:
                    self.error_summary.add_error(extraction_error)
                continue

        logger.info(f"Successfully extracted {len(articles)} articles from {source}")
        return articles
