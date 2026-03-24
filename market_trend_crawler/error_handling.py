"""Error handling utilities for crawler framework.

This module provides comprehensive error handling with:
- Custom exception hierarchy
- Error context and tracking
- Error recovery strategies
- Error aggregation and reporting
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from traceback import format_exc

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severity levels for crawler errors."""

    CRITICAL = "critical"  # System cannot continue
    ERROR = "error"  # Operation failed but can continue
    WARNING = "warning"  # Issue detected but operation succeeded
    INFO = "info"  # Informational message


class ErrorType(Enum):
    """Types of crawler errors."""

    NETWORK = "network"  # HTTP/connection errors
    PARSING = "parsing"  # HTML/XML parsing errors
    EXTRACTION = "extraction"  # Data extraction errors
    VALIDATION = "validation"  # Data validation errors
    TIMEOUT = "timeout"  # Request timeout errors
    RATE_LIMIT = "rate_limit"  # Rate limiting errors
    UNKNOWN = "unknown"  # Uncategorized errors


@dataclass
class ErrorContext:
    """Context information for errors."""

    source: str
    url: Optional[str] = None
    article_index: Optional[int] = None
    field_name: Optional[str] = None
    field_value: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.now)
    additional_info: dict = field(default_factory=dict)


class CrawlerError(Exception):
    """Base exception for all crawler errors."""

    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None,
    ):
        """Initialize crawler error.

        Args:
            message: Error message
            error_type: Type of error
            severity: Severity level
            context: Error context information
            original_exception: Original exception if wrapping
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.context = context
        self.original_exception = original_exception
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        """String representation with context."""
        parts = [f"[{self.error_type.value.upper()}] {self.message}"]

        if self.context:
            parts.append(f"Source: {self.context.source}")
            if self.context.url:
                parts.append(f"URL: {self.context.url}")
            if self.context.article_index is not None:
                parts.append(f"Article Index: {self.context.article_index}")
            if self.context.field_name:
                parts.append(f"Field: {self.context.field_name}")

        return " | ".join(parts)

    def to_dict(self) -> dict:
        """Convert error to dictionary for logging/serialization."""
        return {
            "message": self.message,
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "context": {
                "source": self.context.source if self.context else None,
                "url": self.context.url if self.context else None,
                "article_index": self.context.article_index if self.context else None,
                "field_name": self.context.field_name if self.context else None,
            } if self.context else None,
            "original_exception": str(self.original_exception) if self.original_exception else None,
        }


class NetworkError(CrawlerError):
    """Network-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.ERROR,
            context=context,
            original_exception=original_exception,
        )


class ParsingError(CrawlerError):
    """HTML/XML parsing errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_type=ErrorType.PARSING,
            severity=ErrorSeverity.WARNING,  # Parsing errors are often recoverable
            context=context,
            original_exception=original_exception,
        )


class ExtractionError(CrawlerError):
    """Data extraction errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_type=ErrorType.EXTRACTION,
            severity=ErrorSeverity.WARNING,
            context=context,
            original_exception=original_exception,
        )


class ValidationError(CrawlerError):
    """Data validation errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION,
            severity=ErrorSeverity.WARNING,
            context=context,
            original_exception=original_exception,
        )


class TimeoutError(CrawlerError):
    """Request timeout errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_type=ErrorType.TIMEOUT,
            severity=ErrorSeverity.ERROR,
            context=context,
            original_exception=original_exception,
        )


@dataclass
class ErrorSummary:
    """Summary of errors from a crawling session."""

    total_errors: int = 0
    by_type: dict[ErrorType, int] = field(default_factory=dict)
    by_severity: dict[ErrorSeverity, int] = field(default_factory=dict)
    by_source: dict[str, int] = field(default_factory=dict)
    errors: list[CrawlerError] = field(default_factory=list)

    def add_error(self, error: CrawlerError) -> None:
        """Add an error to the summary."""
        self.total_errors += 1

        # Count by type
        self.by_type[error.error_type] = self.by_type.get(error.error_type, 0) + 1

        # Count by severity
        self.by_severity[error.severity] = self.by_severity.get(error.severity, 0) + 1

        # Count by source
        if error.context:
            self.by_source[error.context.source] = self.by_source.get(error.context.source, 0) + 1

        # Store error
        self.errors.append(error)

    def get_stats(self) -> dict:
        """Get summary statistics."""
        return {
            "total_errors": self.total_errors,
            "by_type": {k.value: v for k, v in self.by_type.items()},
            "by_severity": {k.value: v for k, v in self.by_severity.items()},
            "by_source": self.by_source,
        }

    def log_summary(self, log_level: int = logging.WARNING) -> None:
        """Log the error summary."""
        if self.total_errors == 0:
            logger.info("No errors encountered")
            return

        logger.log(
            log_level,
            f"Error Summary: {self.total_errors} total errors\n"
            f"  By Type: {self.by_type}\n"
            f"  By Severity: {self.by_severity}\n"
            f"  By Source: {self.by_source}"
        )


def handle_exception(
    exception: Exception,
    context: ErrorContext,
    default_error_type: ErrorType = ErrorType.UNKNOWN,
    default_severity: ErrorSeverity = ErrorSeverity.ERROR,
) -> CrawlerError:
    """Convert a generic exception into a CrawlerError.

    Args:
        exception: The exception to handle
        context: Error context information
        default_error_type: Default error type if cannot determine
        default_severity: Default severity level

    Returns:
        CrawlerError with appropriate type and context
    """
    # Map common exception types to error types
    error_type = default_error_type
    exception_name = type(exception).__name__

    if exception_name in ["HTTPStatusError", "RequestError", "ConnectionError"]:
        error_type = ErrorType.NETWORK
    elif exception_name in ["TimeoutException"]:
        error_type = ErrorType.TIMEOUT
    elif "Parsing" in exception_name or "Parse" in exception_name:
        error_type = ErrorType.PARSING

    # Create appropriate error
    if error_type == ErrorType.NETWORK:
        return NetworkError(
            message=str(exception),
            context=context,
            original_exception=exception,
        )
    elif error_type == ErrorType.TIMEOUT:
        return TimeoutError(
            message=str(exception),
            context=context,
            original_exception=exception,
        )
    elif error_type == ErrorType.PARSING:
        return ParsingError(
            message=str(exception),
            context=context,
            original_exception=exception,
        )
    else:
        return CrawlerError(
            message=str(exception),
            error_type=error_type,
            severity=default_severity,
            context=context,
            original_exception=exception,
        )


def log_error(
    error: CrawlerError,
    include_traceback: bool = False,
    level: int = logging.WARNING,
) -> None:
    """Log a crawler error with appropriate details.

    Args:
        error: The crawler error to log
        include_traceback: Whether to include traceback
        level: Log level to use
    """
    log_message = str(error)

    if include_traceback and error.original_exception:
        traceback_str = format_exc()
        log_message += f"\nTraceback:\n{traceback_str}"

    logger.log(level, log_message)


def create_error_context(
    source: str,
    url: Optional[str] = None,
    article_index: Optional[int] = None,
    field_name: Optional[str] = None,
    field_value: Optional[Any] = None,
    **kwargs,
) -> ErrorContext:
    """Create an ErrorContext object with common fields.

    Args:
        source: Source name
        url: URL being processed
        article_index: Index of article being processed
        field_name: Name of field being processed
        field_value: Value of field being processed
        **kwargs: Additional context information

    Returns:
        ErrorContext object
    """
    return ErrorContext(
        source=source,
        url=url,
        article_index=article_index,
        field_name=field_name,
        field_value=field_value,
        additional_info=kwargs,
    )
