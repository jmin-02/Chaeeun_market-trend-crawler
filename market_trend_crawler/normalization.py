"""Data normalization utilities for crawler framework.

This module provides comprehensive data normalization with:
- URL normalization and validation
- Text cleaning and normalization
- Date/time normalization and validation
- HTML content cleaning
- Data validation and sanitization
"""

import logging
import re
from datetime import datetime, timezone
from html import unescape
from typing import Optional, Any
from urllib.parse import urlparse, urljoin, urlunparse

import bs4
from pydantic import HttpUrl, ValidationError

from .models import Article, Category, SourceLanguage

logger = logging.getLogger(__name__)


class NormalizationError(Exception):
    """Exception raised during data normalization."""

    pass


# Regex patterns for normalization
WHITESPACE_PATTERN = re.compile(r"\s+")
EXTRA_NEWLINES_PATTERN = re.compile(r"\n{3,}")
MULTIPLE_SPACES_PATTERN = re.compile(r" {2,}")
UNICODE_WHITESPACE_PATTERN = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\u2060\ufeff]")
TRACKING_PARAM_PATTERN = re.compile(r"^(utm_[^&]*|fbclid|ref|source|gclid)=", re.IGNORECASE)


def normalize_url(url: str, base_url: Optional[str] = None, remove_tracking: bool = True) -> str:
    """Normalize a URL.

    Args:
        url: URL to normalize
        base_url: Base URL for resolving relative URLs
        remove_tracking: Whether to remove tracking parameters

    Returns:
        Normalized URL

    Raises:
        NormalizationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise NormalizationError(f"Invalid URL: {url}")

    try:
        # Handle relative URLs
        if base_url and not url.startswith(("http://", "https://", "//")):
            url = urljoin(base_url, url)

        # Parse URL
        parsed = urlparse(url)

        # Scheme and netloc validation
        if not parsed.scheme or not parsed.netloc:
            raise NormalizationError(f"URL missing scheme or netloc: {url}")

        # Normalize scheme to lowercase
        scheme = parsed.scheme.lower()

        # Normalize netloc to lowercase
        netloc = parsed.netloc.lower()

        # Remove default ports
        if (scheme == "http" and netloc.endswith(":80")) or (
            scheme == "https" and netloc.endswith(":443")
        ):
            netloc = netloc.rsplit(":", 1)[0]

        # Normalize path
        path = parsed.path
        # Remove trailing slash for non-root paths
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        # Remove tracking parameters from query
        query = parsed.query
        if remove_tracking and query:
            # Remove tracking parameters while preserving other query params
            parts = []
            for param in query.split("&"):
                if param and not TRACKING_PARAM_PATTERN.match(param):
                    parts.append(param)
            query = "&".join(parts)
            if query == "":
                query = ""

        # Reconstruct URL
        normalized = urlunparse((scheme, netloc, path, "", query, ""))

        return normalized

    except Exception as e:
        raise NormalizationError(f"Failed to normalize URL '{url}': {e}") from e


def validate_url(url: str) -> bool:
    """Validate a URL using pydantic HttpUrl.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        HttpUrl(url)
        return True
    except (ValidationError, ValueError):
        return False


def normalize_text(text: Optional[str], strip_html: bool = True, max_length: Optional[int] = None) -> Optional[str]:
    """Normalize text content.

    Args:
        text: Text to normalize
        strip_html: Whether to strip HTML tags
        max_length: Maximum length of text (None for no limit)

    Returns:
        Normalized text or None if input is invalid
    """
    if not text or not isinstance(text, str):
        return None

    try:
        # Decode HTML entities
        text = unescape(text)

        # Strip HTML if requested
        if strip_html:
            text = re.sub(r"<[^>]+>", " ", text)

        # Remove Unicode whitespace characters
        text = UNICODE_WHITESPACE_PATTERN.sub(" ", text)

        # Normalize whitespace
        text = WHITESPACE_PATTERN.sub(" ", text)

        # Remove extra newlines
        text = EXTRA_NEWLINES_PATTERN.sub("\n\n", text)

        # Remove multiple spaces
        text = MULTIPLE_SPACES_PATTERN.sub(" ", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        # Truncate if max_length specified
        if max_length and len(text) > max_length:
            text = text[:max_length].rsplit(" ", 1)[0] + "..."

        return text

    except Exception as e:
        logger.warning(f"Failed to normalize text: {e}")
        return None


def normalize_title(title: Optional[str]) -> Optional[str]:
    """Normalize article title.

    Args:
        title: Title to normalize

    Returns:
        Normalized title or None if invalid
    """
    return normalize_text(title, strip_html=True, max_length=500)


def normalize_content(content: Optional[str], preserve_paragraphs: bool = True) -> Optional[str]:
    """Normalize article content.

    Args:
        content: Content to normalize
        preserve_paragraphs: Whether to preserve paragraph structure

    Returns:
        Normalized content or None if invalid
    """
    if preserve_paragraphs:
        # Preserve paragraph structure
        content = normalize_text(content, strip_html=False)
        if content:
            # Limit to reasonable length
            content = content[:10000]
    else:
        content = normalize_text(content, strip_html=True)

    return content


def normalize_datetime(
    dt_str: Optional[str],
    timezone_str: Optional[str] = None,
    default: Optional[datetime] = None,
) -> Optional[datetime]:
    """Normalize a datetime string to datetime object.

    Args:
        dt_str: Datetime string to parse
        timezone_str: Optional timezone to apply
        default: Default datetime if parsing fails

    Returns:
        Normalized datetime object or default/None
    """
    if not dt_str or not isinstance(dt_str, str):
        return default

    # Common datetime formats
    formats = [
        # ISO format
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        # Korean formats
        "%Y.%m.%d %H:%M",
        "%Y.%m.%d",
        "%Y년 %m월 %d일",
        # US formats
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        # Other formats
        "%d %B %Y",
        "%d %b %Y",
    ]

    # Try parsing with various formats
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            # Apply timezone if specified
            if timezone_str and dt.tzinfo is None:
                # This is simplified - in production you'd use pytz or zoneinfo
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            continue

    # Try ISO format with timezone
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt
    except (ValueError, AttributeError):
        pass

    logger.warning(f"Failed to parse datetime string: {dt_str}")
    return default


def normalize_author(author: Optional[str]) -> Optional[str]:
    """Normalize author name.

    Args:
        author: Author name to normalize

    Returns:
        Normalized author name or None if invalid
    """
    return normalize_text(author, strip_html=True, max_length=200)


def normalize_tags(tags: Optional[list[str]]) -> list[str]:
    """Normalize article tags.

    Args:
        tags: List of tags to normalize

    Returns:
        List of normalized tags
    """
    if not tags or not isinstance(tags, list):
        return []

    normalized = []
    seen = set()

    for tag in tags:
        if not isinstance(tag, str):
            continue

        # Normalize tag
        norm_tag = normalize_text(tag, strip_html=True, max_length=100)
        if norm_tag and norm_tag.lower() not in seen:
            seen.add(norm_tag.lower())
            normalized.append(norm_tag)

    return normalized


def validate_article(article: Article) -> tuple[bool, list[str]]:
    """Validate an article object.

    Args:
        article: Article to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Validate title
    if not article.title or len(article.title) < 5:
        errors.append(f"Invalid title: '{article.title}'")

    # Validate URL
    if not validate_url(str(article.url)):
        errors.append(f"Invalid URL: '{article.url}'")

    # Validate content
    if not article.content or len(article.content) < 10:
        errors.append(f"Invalid content: length={len(article.content) if article.content else 0}")

    # Validate category
    if not isinstance(article.category, Category):
        errors.append(f"Invalid category: '{article.category}'")

    # Validate source
    if not article.source or len(article.source) < 2:
        errors.append(f"Invalid source: '{article.source}'")

    # Validate datetime
    if not isinstance(article.published_at, datetime):
        errors.append(f"Invalid published_at: '{article.published_at}'")

    # Validate language
    if not isinstance(article.language, SourceLanguage):
        errors.append(f"Invalid language: '{article.language}'")

    return len(errors) == 0, errors


def normalize_article(
    article: Article,
    base_url: Optional[str] = None,
    remove_tracking: bool = True,
) -> Article:
    """Normalize an article object.

    Args:
        article: Article to normalize
        base_url: Base URL for resolving relative URLs
        remove_tracking: Whether to remove tracking parameters from URLs

    Returns:
        Normalized article (may modify in place)

    Raises:
        NormalizationError: If normalization fails critically
    """
    try:
        # Normalize URL
        normalized_url = normalize_url(str(article.url), base_url=base_url, remove_tracking=remove_tracking)
        article.url = HttpUrl(normalized_url)  # This will validate

        # Normalize title
        article.title = normalize_title(article.title) or "Untitled"

        # Normalize content
        article.content = normalize_content(article.content) or ""

        # Normalize author
        article.author = normalize_author(article.author)

        # Normalize tags
        article.tags = normalize_tags(article.tags)

        # Validate article
        is_valid, errors = validate_article(article)
        if not is_valid:
            raise NormalizationError(f"Article validation failed: {', '.join(errors)}")

        return article

    except Exception as e:
        logger.error(f"Failed to normalize article: {e}")
        raise NormalizationError(f"Article normalization failed: {e}") from e


def clean_html_content(html: str, preserve_links: bool = True) -> str:
    """Clean HTML content while preserving structure.

    Args:
        html: HTML content to clean
        preserve_links: Whether to preserve link tags

    Returns:
        Cleaned text content
    """
    if not html or not isinstance(html, str):
        return ""

    try:
        soup = bs4.BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        # Get text
        text = soup.get_text()

        # Normalize whitespace
        text = WHITESPACE_PATTERN.sub(" ", text)
        text = text.strip()

        return text

    except Exception as e:
        logger.warning(f"Failed to clean HTML: {e}")
        return normalize_text(html, strip_html=True)


def extract_text_length(text: Optional[str]) -> int:
    """Extract length of text with proper handling.

    Args:
        text: Text to measure

    Returns:
        Length of text or 0 if None
    """
    if not text or not isinstance(text, str):
        return 0
    return len(text)


def sanitize_field(value: Any, max_length: Optional[int] = None) -> Optional[str]:
    """Sanitize a field value to string.

    Args:
        value: Value to sanitize
        max_length: Maximum length

    Returns:
        Sanitized string or None
    """
    if value is None:
        return None

    # Convert to string
    text = str(value)

    # Normalize
    text = normalize_text(text, strip_html=True, max_length=max_length)

    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)].rsplit(" ", 1)[0] + suffix
