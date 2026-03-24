"""Base crawler with retry, rate limiting, and comprehensive error handling."""

import asyncio
import logging
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import httpx
from pydantic import BaseModel

from .error_handling import (
    CrawlerError,
    ErrorContext,
    ErrorSummary,
    ErrorType,
    NetworkError,
    TimeoutError,
    handle_exception,
    log_error,
)
from .models import Article, Category
from .normalization import (
    normalize_article,
    validate_article,
)

logger = logging.getLogger(__name__)


@dataclass
class CrawlerConfig:
    """Configuration for crawler behavior."""

    rate_limit: float = 2.0  # Seconds between requests
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    respect_robots_txt: bool = True
    backoff_factor: float = 2.0
    jitter: bool = True
    max_jitter: float = 1.0

    # Error handling options
    enable_data_normalization: bool = True
    validate_articles: bool = True
    log_extraction_errors: bool = True
    log_validation_errors: bool = True
    include_error_traceback: bool = False
    max_error_tolerance: int = 10  # Max errors before stopping

    # Normalization options
    remove_tracking_params: bool = True
    max_title_length: int = 500
    max_content_length: int = 10000
    max_author_length: int = 200
    max_tags: int = 10


class CrawlError(Exception):
    """Base exception for crawling errors."""

    pass


class MaxRetriesExceededError(CrawlError):
    """Raised when max retries exceeded."""

    pass


class RateLimitError(CrawlError):
    """Raised when rate limit is hit."""

    pass


class BaseCrawler:
    """Base crawler with retry and rate limiting.

    Provides:
    - Exponential backoff retry mechanism
    - Rate limiting between requests
    - User agent rotation support
    - Timeout handling
    - Error logging

    Subclasses must implement extract_articles method.
    """

    def __init__(
        self,
        config: Optional[CrawlerConfig] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Initialize crawler.

        Args:
            config: Crawler configuration
            client: Optional httpx client for testing
        """
        self.config = config or CrawlerConfig()
        self.client = client or httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={"User-Agent": self.config.user_agent},
        )
        self._last_request_time: Optional[datetime] = None
        self._request_count = 0
        self._success_count = 0
        self._failure_count = 0
        self.session_id = str(uuid.uuid4())
        self.error_summary = ErrorSummary()
        self._start_time = datetime.now()

    async def _wait_for_rate_limit(self) -> None:
        """Wait based on rate limit setting."""
        if self._last_request_time is None:
            return

        elapsed = (datetime.now() - self._last_request_time).total_seconds()
        wait_time = self.config.rate_limit - elapsed

        if wait_time > 0:
            if self.config.jitter:
                jitter = random.uniform(0, self.config.max_jitter)
                wait_time += jitter

            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

    async def _fetch_with_retry(self, url: str) -> str:
        """Fetch URL with retry logic.

        Args:
            url: URL to fetch

        Returns:
            HTML content

        Raises:
            MaxRetriesExceededError: If max retries exceeded
        """
        retry_count = 0
        last_error: Optional[Exception] = None

        while retry_count < self.config.max_retries:
            try:
                await self._wait_for_rate_limit()

                response = await self.client.get(url)
                response.raise_for_status()

                self._last_request_time = datetime.now()
                self._request_count += 1
                self._success_count += 1

                logger.info(
                    f"[{self.session_id[:8]}] Successfully fetched {url} (attempt {retry_count + 1})"
                )
                return response.text

            except httpx.HTTPStatusError as e:
                last_error = e
                retry_count += 1

                # Create error context
                error_context = ErrorContext(
                    source=self.__class__.__name__,
                    url=url,
                    additional_info={
                        "attempt": retry_count,
                        "status_code": e.response.status_code,
                    },
                )

                if e.response.status_code == 429:
                    # Rate limited - wait longer
                    backoff = self.config.backoff_factor ** (retry_count + 1)
                    logger.warning(
                        f"[{self.session_id[:8]}] Rate limited on {url}, waiting {backoff:.2f}s before retry {retry_count}"
                    )
                    await asyncio.sleep(backoff)
                elif 500 <= e.response.status_code < 600:
                    # Server error - retry with backoff
                    backoff = self.config.backoff_factor ** retry_count
                    logger.warning(
                        f"[{self.session_id[:8]}] Server error {e.response.status_code} on {url}, "
                        f"retrying in {backoff:.2f}s (attempt {retry_count})"
                    )
                    await asyncio.sleep(backoff)
                else:
                    # Client error - don't retry
                    client_error = handle_exception(e, error_context)
                    self._failure_count += 1
                    self.error_summary.add_error(client_error)
                    log_error(client_error, include_traceback=self.config.include_error_traceback)
                    raise CrawlerError(f"HTTP {e.response.status_code}: {e}") from e

            except httpx.TimeoutException as e:
                last_error = e
                retry_count += 1
                backoff = self.config.backoff_factor ** retry_count

                error_context = ErrorContext(
                    source=self.__class__.__name__,
                    url=url,
                    additional_info={"attempt": retry_count},
                )

                timeout_error = TimeoutError(
                    message=f"Request timeout after {self.config.timeout}s",
                    context=error_context,
                    original_exception=e,
                )

                logger.warning(
                    f"[{self.session_id[:8]}] Timeout on {url}, retrying in {backoff:.2f}s (attempt {retry_count})"
                )
                await asyncio.sleep(backoff)

            except httpx.RequestError as e:
                last_error = e
                retry_count += 1
                backoff = self.config.backoff_factor ** retry_count

                error_context = ErrorContext(
                    source=self.__class__.__name__,
                    url=url,
                    additional_info={"attempt": retry_count},
                )

                network_error = NetworkError(
                    message=f"Request error: {e}",
                    context=error_context,
                    original_exception=e,
                )

                self.error_summary.add_error(network_error)
                logger.warning(
                    f"[{self.session_id[:8]}] Request error on {url}: {e}, retrying in {backoff:.2f}s (attempt {retry_count})"
                )
                await asyncio.sleep(backoff)

        # All retries exhausted
        self._failure_count += 1

        error_context = ErrorContext(
            source=self.__class__.__name__,
            url=url,
            additional_info={"total_attempts": self.config.max_retries},
        )

        max_retries_error = CrawlerError(
            message=f"Max retries exceeded",
            error_type=ErrorType.UNKNOWN,
            context=error_context,
            original_exception=last_error,
        )

        self.error_summary.add_error(max_retries_error)
        logger.error(f"[{self.session_id[:8]}] Max retries ({self.config.max_retries}) exceeded for {url}")
        raise MaxRetriesExceededError(
            f"Failed to fetch {url} after {self.config.max_retries} attempts"
        ) from last_error

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from HTML content.

        Must be implemented by subclasses.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement extract_articles")

    async def crawl(self, url: str, source: str, language: str = "en") -> list[Article]:
        """Crawl a URL and extract articles.

        Args:
            url: URL to crawl
            source: Source name
            language: Content language

        Returns:
            List of extracted and normalized articles
        """
        logger.info(f"[{self.session_id[:8]}] Starting crawl: {source} - {url}")

        try:
            # Fetch HTML content
            html = await self._fetch_with_retry(url)

            # Extract articles
            logger.debug(f"[{self.session_id[:8]}] Extracting articles from {url}")
            articles = self.extract_articles(html, source, language)

            if not articles:
                logger.warning(f"[{self.session_id[:8]}] No articles extracted from {url}")
                return []

            logger.info(f"[{self.session_id[:8]}] Extracted {len(articles)} articles from {url}")

            # Normalize and validate articles if enabled
            if self.config.enable_data_normalization:
                normalized_articles = []
                validation_failures = 0

                for idx, article in enumerate(articles):
                    try:
                        # Normalize article
                        normalized_article = normalize_article(
                            article,
                            base_url=url,
                            remove_tracking=self.config.remove_tracking_params,
                        )

                        # Validate article if enabled
                        if self.config.validate_articles:
                            is_valid, errors = validate_article(normalized_article)
                            if not is_valid:
                                validation_failures += 1

                                error_context = ErrorContext(
                                    source=source,
                                    url=str(article.url),
                                    article_index=idx,
                                    additional_info={"validation_errors": errors},
                                )

                                validation_error = CrawlerError(
                                    message=f"Article validation failed: {', '.join(errors)}",
                                    error_type=ErrorType.VALIDATION,
                                    context=error_context,
                                )

                                if self.config.log_validation_errors:
                                    log_error(
                                        validation_error,
                                        include_traceback=self.config.include_error_traceback,
                                    )

                                self.error_summary.add_error(validation_error)
                                continue

                        normalized_articles.append(normalized_article)

                    except Exception as e:
                        logger.warning(
                            f"[{self.session_id[:8]}] Failed to normalize article {idx}: {e}"
                        )

                        error_context = ErrorContext(
                            source=source,
                            url=str(article.url),
                            article_index=idx,
                        )

                        normalization_error = handle_exception(
                            e, error_context, default_error_type=ErrorType.VALIDATION
                        )

                        self.error_summary.add_error(normalization_error)
                        continue

                articles = normalized_articles

                if validation_failures > 0:
                    logger.warning(
                        f"[{self.session_id[:8]}] {validation_failures}/{len(articles)} articles failed validation"
                    )

            # Filter fresh articles (within 24 hours)
            fresh_articles = [a for a in articles if a.is_fresh(24)]

            logger.info(
                f"[{self.session_id[:8]}] Crawling complete: {len(fresh_articles)}/{len(articles)} fresh articles from {url}"
            )

            return fresh_articles

        except CrawlerError:
            # Re-raise crawler errors
            raise
        except Exception as e:
            # Handle unexpected errors
            error_context = ErrorContext(
                source=source,
                url=url,
                additional_info={"language": language},
            )

            unexpected_error = handle_exception(e, error_context)
            self.error_summary.add_error(unexpected_error)

            logger.error(
                f"[{self.session_id[:8]}] Unexpected error during crawl: {e}",
                exc_info=self.config.include_error_traceback,
            )

            raise

    async def close(self) -> None:
        """Close the HTTP client and log session summary."""
        self.log_session_summary()
        await self.client.aclose()

    def get_stats(self) -> dict[str, int | float | dict]:
        """Get crawler statistics.

        Returns:
            Dictionary with comprehensive stats
        """
        duration = (datetime.now() - self._start_time).total_seconds()

        return {
            "session_id": self.session_id,
            "duration_seconds": round(duration, 2),
            "requests": {
                "total": self._request_count,
                "successful": self._success_count,
                "failed": self._failure_count,
                "success_rate": round(
                    self._success_count / self._request_count if self._request_count > 0 else 0, 2
                ),
            },
            "errors": self.error_summary.get_stats(),
            "config": {
                "rate_limit": self.config.rate_limit,
                "max_retries": self.config.max_retries,
                "timeout": self.config.timeout,
                "enable_normalization": self.config.enable_data_normalization,
                "validate_articles": self.config.validate_articles,
            },
        }

    def get_error_summary(self) -> ErrorSummary:
        """Get the error summary for this crawler session.

        Returns:
            ErrorSummary object
        """
        return self.error_summary

    def log_session_summary(self) -> None:
        """Log a summary of the crawler session."""
        stats = self.get_stats()

        logger.info(f"[{self.session_id[:8]}] Crawler Session Summary")
        logger.info(f"[{self.session_id[:8]}] Duration: {stats['duration_seconds']}s")
        logger.info(
            f"[{self.session_id[:8]}] Requests: {stats['requests']['successful']}/{stats['requests']['total']} "
            f"({stats['requests']['success_rate']:.1%} success)"
        )
        logger.info(
            f"[{self.session_id[:8]}] Errors: {self.error_summary.total_errors} total"
        )

        # Log detailed error summary
        self.error_summary.log_summary()

    async def __aenter__(self) -> "BaseCrawler":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
