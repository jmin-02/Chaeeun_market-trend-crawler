"""Kurly (컬리) tech blog crawler.

Kurly is a Korean e-commerce company's engineering blog (HelloWorld).
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


class KurlyCrawler(BaseCrawler):
    """Crawler for Kurly HelloWorld Tech Blog - https://helloworld.kurly.com"""

    BASE_URL = "https://helloworld.kurly.com"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from Kurly HelloWorld tech blog.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Find all post-card list items
        post_items = soup.select("li.post-card")

        logger.debug(f"Found {len(post_items)} post card items to process")

        seen_urls = set()
        idx = 0
        for item in post_items:
            try:
                # Find link inside the post card
                link = item.select_one("a[href]")
                if not link:
                    continue

                href = link.get("href", "").strip()
                if not href:
                    continue

                # Build full URL (relative paths start with /blog/)
                if href.startswith("http"):
                    url = href
                else:
                    url = f"{self.BASE_URL}{href}"

                if url in seen_urls:
                    continue
                seen_urls.add(url)

                # Extract title from heading or link text
                heading = item.select_one("h1, h2, h3, h4")
                if heading:
                    title = heading.get_text(strip=True)
                else:
                    title = link.get_text(strip=True)

                if not title or len(title) < 3:
                    continue

                # Extract content from description if available
                desc = item.select_one("p")
                content = desc.get_text(strip=True) if desc else title

                category = classify_article(url, title)

                article = Article(
                    title=title,
                    url=url,
                    content=content[:500],
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
