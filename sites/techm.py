"""TechM (테크엠) crawler.

TechM is a Korean tech media site covering startups and technology.
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseCrawler
from .error_handling import (
    ExtractionError,
    ErrorContext,
    ErrorType,
    create_error_context,
    handle_exception,
)
from .models import Article, Category, SourceLanguage
from .classification import classify_article

logger = logging.getLogger(__name__)


class TechMCrawler(BaseCrawler):
    """Crawler for TechM (테크엠) - https://techm.kr"""

    BASE_URL = "https://techm.kr"

    def extract_articles(self, html: str, source: str, language: str = "ko") -> list[Article]:
        """Extract articles from TechM with enhanced error handling.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # TechM article list items
        article_items = soup.select(".post-item") or soup.select("article")

        logger.debug(f"Found {len(article_items)} article items to process")

        for idx, item in enumerate(article_items):
            try:
                # Extract title
                title = self._extract_title(item, source, idx)
                if not title:
                    logger.debug(f"Skipping article {idx}: no title found")
                    continue

                # Extract URL
                url = self._extract_url(item, source, idx)
                if not url:
                    logger.debug(f"Skipping article {idx}: no URL found")
                    continue

                # Extract content preview
                content = self._extract_content(item, source, idx, default_title=title)

                # Extract publication date
                published_at = self._extract_date(item, source, idx)

                # Extract author
                author = self._extract_author(item, source, idx)

                # Determine category
                category = self._determine_category(url, title)

                # Create article
                article = Article(
                    title=title,
                    url=url,
                    content=content,
                    source=source,
                    published_at=published_at,
                    author=author,
                    category=category,
                    language=SourceLanguage.KOREAN,
                )

                articles.append(article)
                logger.debug(f"Successfully extracted article {idx}: {title[:50]}...")

            except Exception as e:
                # Handle extraction errors gracefully
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

        logger.info(f"Successfully extracted {len(articles)}/{len(article_items)} articles from {source}")
        return articles

    def _extract_title(self, item, source: str, index: int) -> Optional[str]:
        """Extract article title with error handling."""
        try:
            title_elem = item.find("h2") or item.find("h3") or item.select_one(".title")
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            if not title or len(title) < 3:
                return None

            return title

        except Exception as e:
            error_context = create_error_context(
                source=source, article_index=index, field_name="title"
            )
            raise ExtractionError(
                message="Failed to extract title", context=error_context, original_exception=e
            )

    def _extract_url(self, item, source: str, index: int) -> Optional[str]:
        """Extract article URL with error handling."""
        try:
            link_elem = item.find("a")
            if not link_elem:
                return None

            url = link_elem.get("href", "")

            if not url:
                return None

            # Resolve relative URLs
            if not url.startswith("http"):
                url = f"{self.BASE_URL}{url}"

            return url

        except Exception as e:
            error_context = create_error_context(
                source=source, article_index=index, field_name="url"
            )
            raise ExtractionError(
                message="Failed to extract URL", context=error_context, original_exception=e
            )

    def _extract_content(self, item, source: str, index: int, default_title: str) -> str:
        """Extract article content with error handling."""
        try:
            content_elem = item.select_one(".excerpt") or item.select_one(".content")
            content = content_elem.get_text(strip=True) if content_elem else default_title

            return content[:500]  # Limit content length

        except Exception as e:
            logger.debug(f"Failed to extract content at index {index}, using title as fallback")
            return default_title[:500]

    def _extract_date(self, item, source: str, index: int) -> datetime:
        """Extract article publication date with error handling."""
        try:
            time_elem = item.find("time") or item.select_one(".date") or item.select_one(".time")
            if not time_elem:
                return datetime.now()

            datetime_str = time_elem.get("datetime") or time_elem.get_text(strip=True)
            if not datetime_str:
                return datetime.now()

            # Try ISO format
            try:
                return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

            # Try Korean date format
            try:
                return datetime.strptime(datetime_str, "%Y.%m.%d")
            except ValueError:
                pass

            return datetime.now()

        except Exception as e:
            logger.debug(f"Failed to extract date at index {index}, using current time")
            return datetime.now()

    def _extract_author(self, item, source: str, index: int) -> Optional[str]:
        """Extract article author with error handling."""
        try:
            author_elem = item.select_one(".author") or item.select_one(".writer")
            return author_elem.get_text(strip=True) if author_elem else None

        except Exception as e:
            logger.debug(f"Failed to extract author at index {index}")
            return None

    def _determine_category(self, url: str, title: str) -> Category:
        """Determine category from URL and title using centralized classification.

        Args:
            url: Article URL
            title: Article title

        Returns:
            Category enum value
        """
        return classify_article(url, title)
