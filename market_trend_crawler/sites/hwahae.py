"""Hwahae (화해) tech blog crawler.

Hwahae is a Korean beauty tech company's engineering blog.
"""

import logging
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


class HwahaeCrawler(BaseCrawler):
    """Crawler for Hwahae Tech Blog - https://blog.hwahae.co.kr"""

    BASE_URL = "https://blog.hwahae.co.kr"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from Hwahae tech blog.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Find all links containing /all/tech/ or similar paths
        link_elements = soup.find_all("a", href=True)
        tech_links = [
            link for link in link_elements
            if "/all/tech/" in link.get("href", "") or "/all/" in link.get("href", "")
        ]

        logger.debug(f"Found {len(tech_links)} article links to process")

        seen_urls = set()
        idx = 0
        for link in tech_links:
            try:
                href = link.get("href", "").strip()
                if not href:
                    continue

                # Build full URL
                if href.startswith("http"):
                    url = href
                else:
                    url = f"{self.BASE_URL}{href}"

                if url in seen_urls:
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
