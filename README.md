# Crawler Framework

A comprehensive web crawling framework for automated tech news and blog scraping with built-in retry mechanisms, rate limiting, scheduling, enhanced error handling, and data normalization.

## Features

### Core Features
- **Retry Mechanism**: Exponential backoff retry for failed requests
- **Rate Limiting**: Configurable delays between requests to avoid overwhelming servers
- **Daily Scheduling**: Automated runs at specific times (default: 10 AM and 5 PM)
- **Async Support**: Full async/await support for concurrent crawling
- **Extensible**: Easy to create custom crawlers for different sites

### Enhanced Error Handling (New!)
- **Custom Exception Hierarchy**: Specific exception types for different error scenarios
- **Detailed Error Context**: Track source, URL, article index, and field information
- **Error Aggregation**: Collect and report errors across crawling sessions
- **Graceful Recovery**: Individual article failures don't stop the entire crawl
- **Error Summary Reporting**: Comprehensive statistics on errors by type, severity, and source

### Data Normalization (New!)
- **URL Normalization**: Resolve relative URLs, remove tracking parameters, validate URLs
- **Text Cleaning**: Remove HTML entities, normalize whitespace, truncate content
- **Date/Time Normalization**: Support multiple date formats, handle timezones
- **Article Validation**: Ensure data quality with field validation rules
- **HTML Content Cleaning**: Strip unwanted HTML while preserving structure

### Structured Logging (New!)
- **Session-Based Logging**: Unique session IDs for traceability
- **Per-Article Logging**: Detailed logs for each article extraction
- **Performance Metrics**: Track duration, success rates, and error counts
- **Configurable Log Levels**: Control verbosity of logging output

## Installation

The crawler framework is part of the ouroboros package:

```bash
pip install ouroboros-ai
```

## Quick Start

### Creating a Custom Crawler

```python
from datetime import datetime
from ouroboros.crawler import BaseCrawler, Article, Category, SourceLanguage
from bs4 import BeautifulSoup

class MyNewsCrawler(BaseCrawler):
    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from HTML content."""
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        for item in soup.find_all("article"):
            title = item.find("h2").text.strip()
            url = item.find("a")["href"]
            content = item.find("div", class_="content").text.strip()
            published_str = item.find("time")["datetime"]

            article = Article(
                title=title,
                url=url,
                content=content,
                source=source,
                published_at=datetime.fromisoformat(published_str),
                language=SourceLanguage.KOREAN if language == "ko" else SourceLanguage.ENGLISH,
            )
            articles.append(article)

        return articles
```

### Using the Crawler

```python
import asyncio
from ouroboros.crawler import CrawlerConfig

async def main():
    # Create crawler with custom config
    config = CrawlerConfig(
        rate_limit=2.0,  # 2 seconds between requests
        max_retries=3,
        timeout=30,
    )

    crawler = MyNewsCrawler(config=config)

    try:
        # Crawl a URL
        articles = await crawler.crawl(
            "https://example.com/news",
            source="Example News",
            language="en"
        )

        print(f"Crawled {len(articles)} articles")
        for article in articles:
            print(f"- {article.title}")
            print(f"  {article.url}")
            print(f"  Fresh: {article.is_fresh(24)}")

    finally:
        await crawler.close()

asyncio.run(main())
```

### Using the Daily Scheduler

```python
import asyncio
from datetime import time
from ouroboros.crawler import DailyScheduler, ScheduleConfig, ScheduleTask

async def main():
    # Create scheduler with custom run times
    config = ScheduleConfig(run_times=[time(10, 0), time(17, 0)])

    crawler = MyNewsCrawler()
    scheduler = DailyScheduler(config=config, crawler=crawler)

    # Register tasks
    tasks = [
        ScheduleTask(
            name="Tech News",
            url="https://example.com/news",
            source="Example News",
            language="en",
        ),
        ScheduleTask(
            name="Korean Tech",
            url="https://example.co.kr/news",
            source="Korean Tech",
            language="ko",
        ),
    ]
    scheduler.register_tasks(tasks)

    # Run immediately once
    results = await scheduler.run_once()
    for task_name, articles in results.items():
        print(f"{task_name}: {len(articles)} articles")

    # Or start the scheduler for automatic daily runs
    # await scheduler.start()

asyncio.run(main())
```

## Configuration

### CrawlerConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rate_limit` | float | 2.0 | Seconds between requests |
| `max_retries` | int | 3 | Maximum retry attempts |
| `timeout` | int | 30 | Request timeout in seconds |
| `user_agent` | str | Mozilla/5.0... | HTTP user agent header |
| `respect_robots_txt` | bool | True | Respect robots.txt |
| `backoff_factor` | float | 2.0 | Exponential backoff multiplier |
| `jitter` | bool | True | Add random jitter to delays |
| `max_jitter` | float | 1.0 | Maximum jitter in seconds |
| `enable_data_normalization` | bool | True | Enable data normalization |
| `validate_articles` | bool | True | Validate article data |
| `log_extraction_errors` | bool | True | Log extraction errors |
| `log_validation_errors` | bool | True | Log validation errors |
| `include_error_traceback` | bool | False | Include traceback in error logs |
| `max_error_tolerance` | int | 10 | Max errors before stopping |
| `remove_tracking_params` | bool | True | Remove tracking parameters from URLs |
| `max_title_length` | int | 500 | Maximum title length |
| `max_content_length` | int | 10000 | Maximum content length |
| `max_author_length` | int | 200 | Maximum author length |
| `max_tags` | int | 10 | Maximum number of tags |

### ScheduleConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `run_times` | list[time] | [10:00, 17:00] | Daily run times |

## Data Models

### Article

Represents a crawled article with fields:
- `title`: Article title
- `url`: Article URL
- `content`: Article content
- `summary`: Optional summary
- `category`: Article category (enum)
- `source`: Source name
- `published_at`: Publication datetime
- `crawled_at`: Crawl datetime
- `author`: Optional author
- `tags`: List of tags
- `language`: Content language

### Category

Available categories:
- `AI_ML`: AI and Machine Learning
- `WEB3_BLOCKCHAIN`: Web3 and Blockchain
- `STARTUP`: Startups
- `DEVELOPMENT`: Software Development
- `SECURITY`: Cybersecurity
- `HARDWARE`: Hardware
- `MOBILE`: Mobile Technology
- `CLOUD`: Cloud Computing
- `DATA`: Data Science
- `PRODUCTIVITY`: Productivity Tools
- `OTHER`: Other

### Source

Configuration for a source site:
- `name`: Site name
- `url`: Site URL
- `language`: Content language
- `category_mapping`: Optional URL pattern to category mapping
- `enabled`: Whether source is active

## Error Handling

The crawler handles various error scenarios:

### HTTP Errors
- **429 Rate Limit**: Automatically retries with longer backoff
- **5xx Server Errors**: Retries with exponential backoff
- **4xx Client Errors**: Does not retry (except 429)
- **Timeouts**: Retries with backoff
- **Max Retries Exceeded**: Raises `MaxRetriesExceededError`

### Enhanced Error Handling
The framework includes a comprehensive error handling system:

```python
from ouroboros.crawler.error_handling import (
    CrawlerError,
    NetworkError,
    ParsingError,
    ExtractionError,
    ValidationError,
    ErrorContext,
    create_error_context,
    log_error,
)

# Create error context
error_context = create_error_context(
    source="Bloter",
    url="https://www.bloter.net/article/1",
    article_index=5,
    field_name="title",
)

# Log error
log_error(error, include_traceback=True)

# Get error summary
error_summary = crawler.get_error_summary()
error_summary.log_summary()
```

### Error Types

- `NetworkError`: HTTP/connection errors
- `ParsingError`: HTML/XML parsing errors
- `ExtractionError`: Data extraction errors
- `ValidationError`: Data validation errors
- `TimeoutError`: Request timeout errors
- `RateLimitError`: Rate limiting errors

### Error Severity Levels

- `CRITICAL`: System cannot continue
- `ERROR`: Operation failed but can continue
- `WARNING`: Issue detected but operation succeeded
- `INFO`: Informational message

## Data Normalization

The framework automatically normalizes and validates article data:

### URL Normalization

```python
from ouroboros.crawler.normalization import normalize_url

# Normalize URL (resolves relative, removes tracking)
url = normalize_url(
    "https://example.com/path/?utm_source=test",
    base_url="https://example.com",
    remove_tracking=True
)
# Result: "https://example.com/path"
```

### Text Normalization

```python
from ouroboros.crawler.normalization import normalize_text, normalize_title

# Normalize text
title = normalize_text("  Example  Title  ", strip_html=True, max_length=100)
# Result: "Example Title"

# Normalize title
title = normalize_title("  Article Title  ")
# Result: "Article Title"
```

### Date/Time Normalization

```python
from ouroboros.crawler.normalization import normalize_datetime

# Normalize datetime (supports multiple formats)
dt = normalize_datetime("2024.03.24 10:30")
dt = normalize_datetime("2024-03-24T10:30:00Z")
dt = normalize_datetime("March 24, 2024")
```

### Article Validation

```python
from ouroboros.crawler.normalization import validate_article, normalize_article

# Normalize article
article = normalize_article(
    article,
    base_url="https://example.com",
    remove_tracking=True
)

# Validate article
is_valid, errors = validate_article(article)
if not is_valid:
    print(f"Validation errors: {errors}")
```

## Freshness Filter

Articles are automatically filtered to include only fresh content (within 24 hours by default):

```python
# Check if article is fresh
article.is_fresh(hours=24)  # True if within 24 hours
```

## Statistics

### Crawler Statistics

Get comprehensive crawler statistics:

```python
# Crawler stats
stats = crawler.get_stats()
# {
#     "session_id": "abc12345-...",
#     "duration_seconds": 15.23,
#     "requests": {
#         "total": 100,
#         "successful": 95,
#         "failed": 5,
#         "success_rate": 0.95
#     },
#     "errors": {
#         "total_errors": 5,
#         "by_type": {
#             "extraction": 3,
#             "validation": 2
#         },
#         "by_severity": {
#             "warning": 4,
#             "error": 1
#         },
#         "by_source": {
#             "Bloter": 2,
#             "TechM": 3
#         }
#     },
#     "config": {
#         "rate_limit": 2.0,
#         "max_retries": 3,
#         "timeout": 30,
#         "enable_normalization": true,
#         "validate_articles": true
#     }
# }
```

### Error Summary

Get detailed error summary:

```python
# Get error summary
error_summary = crawler.get_error_summary()

# Log summary
error_summary.log_summary()

# Get stats
stats = error_summary.get_stats()
print(f"Total errors: {stats['total_errors']}")
print(f"By type: {stats['by_type']}")
print(f"By severity: {stats['by_severity']}")
```

### Session Summary

Log a summary of the crawler session:

```python
crawler.log_session_summary()
# Output:
# [abc12345] Crawler Session Summary
# [abc12345] Duration: 15.23s
# [abc12345] Requests: 95/100 (95.0% success)
# [abc12345] Errors: 5 total
```

### Scheduler Statistics

Get scheduler statistics:

```python
# Scheduler stats
stats = scheduler.get_stats()
# {
#     "scheduler": {
#         "total_tasks": 10,
#         "enabled_tasks": 8,
#         "running": False,
#         "run_times": ["10:00", "17:00"]
#     },
#     "crawler": {...}
# }
```

## Testing

Run the unit tests:

```bash
pytest tests/unit/crawler/ -v
```

## License

Part of the Ouroboros AI Workflow System project.

## Documentation

For detailed information on enhanced error handling and data normalization, see:

- [ENHANCED_ERROR_HANDLING.md](ENHANCED_ERROR_HANDLING.md) - Comprehensive guide on error handling, logging, and data normalization
