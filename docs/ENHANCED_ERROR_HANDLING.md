# Enhanced Error Handling and Data Normalization Guide

This document explains the enhanced error handling, logging, and data normalization features implemented across all crawlers.

## Overview

The crawler framework now includes:

1. **Comprehensive Error Handling**
   - Custom exception hierarchy with specific error types
   - Detailed error context tracking
   - Error aggregation and reporting
   - Graceful error recovery

2. **Structured Logging**
   - Session-based logging with unique IDs
   - Per-article extraction logging
   - Performance metrics tracking
   - Configurable log levels

3. **Data Normalization**
   - URL normalization and validation
   - Text cleaning and standardization
   - Date/time normalization
   - HTML content cleaning
   - Article validation

## Error Handling Architecture

### Exception Hierarchy

```python
CrawlerError (base)
├── NetworkError
├── ParsingError
├── ExtractionError
├── ValidationError
├── TimeoutError
└── RateLimitError
```

### Error Types

- **NETWORK**: HTTP/connection errors
- **PARSING**: HTML/XML parsing errors
- **EXTRACTION**: Data extraction errors
- **VALIDATION**: Data validation errors
- **TIMEOUT**: Request timeout errors
- **RATE_LIMIT**: Rate limiting errors

### Error Severity Levels

- **CRITICAL**: System cannot continue
- **ERROR**: Operation failed but can continue
- **WARNING**: Issue detected but operation succeeded
- **INFO**: Informational message

## Error Context

Each error includes detailed context:

```python
@dataclass
class ErrorContext:
    source: str                          # Crawler name
    url: Optional[str] = None           # URL being processed
    article_index: Optional[int] = None  # Article index
    field_name: Optional[str] = None    # Field being extracted
    field_value: Optional[Any] = None    # Value of field
    timestamp: datetime = ...           # When error occurred
    additional_info: dict = ...         # Additional context
```

## Data Normalization Features

### URL Normalization

- Resolves relative URLs to absolute URLs
- Normalizes scheme and netloc to lowercase
- Removes default ports (80 for HTTP, 443 for HTTPS)
- Removes trailing slashes from non-root paths
- Removes tracking parameters (utm_*, fbclid, ref, etc.)
- Validates URLs using pydantic HttpUrl

### Text Normalization

- Decodes HTML entities
- Strips HTML tags (optional)
- Removes Unicode whitespace characters
- Normalizes whitespace to single spaces
- Removes excessive newlines
- Truncates to max length with ellipsis

### Date/Time Normalization

- Supports multiple date formats:
  - ISO format: `2024-03-24T10:30:00`
  - Korean format: `2024.03.24 10:30`
  - US formats: `03/24/2024 10:30 AM`
  - Natural language: `March 24, 2024`
- Handles timezone conversion
- Defaults to current time if parsing fails

### Article Validation

Validates required fields:
- Title: minimum 5 characters
- URL: valid HTTP/HTTPS URL
- Content: minimum 10 characters
- Category: valid Category enum
- Source: minimum 2 characters
- Language: valid SourceLanguage enum
- Published Date: valid datetime object
- Tags: max 50 tags

## Configuration Options

### CrawlerConfig

```python
@dataclass
class CrawlerConfig:
    rate_limit: float = 2.0
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = ...
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
    max_error_tolerance: int = 10

    # Normalization options
    remove_tracking_params: bool = True
    max_title_length: int = 500
    max_content_length: int = 10000
    max_author_length: int = 200
    max_tags: int = 10
```

## Crawler Template

Here's a template for implementing crawlers with enhanced error handling:

```python
"""[Site Name] crawler.

[Brief description of the site].
"""

import logging
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ouroboros.crawler.base import BaseCrawler
from ouroboros.crawler.error_handling import (
    ExtractionError,
    ErrorContext,
    ErrorType,
    create_error_context,
    handle_exception,
)
from ouroboros.crawler.models import Article, Category, SourceLanguage

logger = logging.getLogger(__name__)


class SiteNameCrawler(BaseCrawler):
    """Crawler for [Site Name] - https://example.com"""

    BASE_URL = "https://example.com"

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from [Site Name] with enhanced error handling.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Select article items based on site's HTML structure
        article_items = soup.select(".article-item") or soup.select("article")

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
                    language=SourceLanguage.ENGLISH,  # or SourceLanguage.KOREAN
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
            time_elem = item.find("time") or item.select_one(".date")
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

            # Try other formats as needed
            # ...

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
        """Determine category from URL and title."""
        url_lower = url.lower()
        title_lower = title.lower()

        # Add site-specific category logic
        if any(k in url_lower or k in title_lower for k in ["ai", "artificial intelligence"]):
            return Category.AI_ML
        if any(k in url_lower or k in title_lower for k in ["blockchain", "web3"]):
            return Category.WEB3_BLOCKCHAIN
        if any(k in url_lower or k in title_lower for k in ["startup", "venture"]):
            return Category.STARTUP

        return Category.OTHER
```

## Usage Examples

### Basic Usage

```python
from ouroboros.crawler import BloterCrawler

# Default configuration
crawler = BloterCrawler()

try:
    articles = await crawler.crawl("https://www.bloter.net", "Bloter", "ko")
    print(f"Extracted {len(articles)} articles")
finally:
    await crawler.close()

# Get statistics
stats = crawler.get_stats()
print(f"Success rate: {stats['requests']['success_rate']:.1%}")
print(f"Errors: {stats['errors']['total_errors']}")
```

### Custom Configuration

```python
from ouroboros.crawler import BloterCrawler, CrawlerConfig

# Custom configuration
config = CrawlerConfig(
    rate_limit=3.0,  # Slower rate
    max_retries=5,   # More retries
    enable_data_normalization=True,
    validate_articles=True,
    log_extraction_errors=True,
    log_validation_errors=True,
    include_error_traceback=True,
)

crawler = BloterCrawler(config=config)
```

### Error Summary

```python
from ouroboros.crawler import BloterCrawler

crawler = BloterCrawler()

try:
    articles = await crawler.crawl("https://www.bloter.net", "Bloter", "ko")
finally:
    await crawler.close()

# Get error summary
error_summary = crawler.get_error_summary()
error_summary.log_summary()

# Get detailed stats
stats = crawler.get_stats()
print(f"Total errors: {stats['errors']['total_errors']}")
print(f"By type: {stats['errors']['by_type']}")
print(f"By source: {stats['errors']['by_source']}")
```

### Data Normalization

```python
from ouroboros.crawler.normalization import (
    normalize_url,
    normalize_text,
    normalize_datetime,
)

# Normalize URL
url = normalize_url("https://example.com/path/?utm_source=test", remove_tracking=True)

# Normalize text
title = normalize_text("  Example  Title  ", strip_html=True, max_length=100)

# Normalize datetime
dt = normalize_datetime("2024.03.24 10:30")
```

## Logging

The crawler uses structured logging with session IDs:

```
[abc12345] Starting crawl: Bloter - https://www.bloter.net
[abc12345] Found 50 article items to process
[abc12345] Successfully extracted article 0: Example Title...
[abc12345] Failed to extract article 5: Failed to extract URL
[abc12345] Successfully extracted 45/50 articles from Bloter
[abc12345] Crawler Session Summary
[abc12345] Duration: 15.23s
[abc12345] Requests: 1/1 (100.0% success)
[abc12345] Errors: 5 total
```

## Updating Existing Crawlers

To update an existing crawler to use enhanced error handling:

1. Import required modules:

```python
import logging
from ouroboros.crawler.error_handling import (
    ExtractionError,
    ErrorContext,
    ErrorType,
    create_error_context,
    handle_exception,
)
```

2. Add logger:

```python
logger = logging.getLogger(__name__)
```

3. Add BASE_URL constant:

```python
BASE_URL = "https://example.com"
```

4. Update extract_articles method:
   - Add session-based logging
   - Wrap extraction in try-except
   - Add error context
   - Log extraction errors
   - Add error to summary

5. Create helper methods for each field:
   - `_extract_title()`
   - `_extract_url()`
   - `_extract_content()`
   - `_extract_date()`
   - `_extract_author()`

6. Each helper method should:
   - Have specific error handling
   - Use ErrorContext
   - Return None/defaults on failure
   - Log debug messages

## Benefits

1. **Improved Reliability**: Graceful error handling prevents single failures from stopping entire crawl
2. **Better Debugging**: Detailed error context makes troubleshooting easier
3. **Consistent Data**: Normalization ensures data quality across all sources
4. **Performance Tracking**: Statistics help monitor crawler health
5. **Configurable**: Easy to adjust behavior via configuration
6. **Scalable**: Pattern works for any number of crawlers

## Best Practices

1. Always include error context in exceptions
2. Use specific exception types (NetworkError, ExtractionError, etc.)
3. Log at appropriate levels (DEBUG for details, INFO for progress, WARNING for issues)
4. Validate data before creating Article objects
5. Use helper methods for field extraction
6. Provide sensible defaults when extraction fails
7. Don't let individual article failures stop the entire crawl
8. Use session IDs in logs for tracing

## Troubleshooting

### High Error Rate

If you see many extraction errors:

1. Check if site structure has changed
2. Review error logs for patterns
3. Verify CSS selectors are still correct
4. Check if rate limiting is needed

### Validation Failures

If articles fail validation:

1. Review validation errors in logs
2. Check if normalization is enabled
3. Verify site is providing required fields
4. Consider adjusting validation rules

### Performance Issues

If crawling is slow:

1. Increase rate_limit in config
2. Check for timeout errors
3. Review error logs for retries
4. Consider reducing max_retries

## Future Enhancements

Potential improvements:

- Automatic retry for specific error types
- Circuit breaker pattern for failing sites
- Error rate-based rate limiting
- Automatic CSS selector updates
- Machine learning for category classification
- Content deduplication across sources
- Distributed crawling support
