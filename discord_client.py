"""Discord webhook and bot API client integration.

This module provides functionality for sending messages to Discord via webhooks
and Discord bot API. It handles configuration management, error handling,
and retry logic for reliable message delivery.

Features:
- Discord webhook integration
- Discord bot API support
- Configuration management
- Error handling and retry logic
- Rate limit handling
- Message splitting for long content
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class DiscordMessageType(str, Enum):
    """Types of Discord messages."""

    WEBHOOK = "webhook"
    BOT = "bot"


class DiscordErrorType(str, Enum):
    """Types of Discord errors."""

    INVALID_URL = "INVALID_URL"
    NETWORK_ERROR = "NETWORK_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class DiscordError:
    """Error details for Discord operations."""

    error_type: DiscordErrorType
    message: str
    status_code: Optional[int] = None
    response_text: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"{self.error_type.value}: {self.message}"


@dataclass
class DiscordConfig:
    """Configuration for Discord webhook/bot integration."""

    webhook_url: Optional[str] = None
    bot_token: Optional[str] = None
    channel_id: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    timeout: float = 30.0  # seconds

    # Message settings
    max_message_length: int = 2000  # Discord's limit
    split_long_messages: bool = True

    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # At least one of webhook_url or bot_token must be provided
        if not self.webhook_url and not self.bot_token:
            errors.append(
                "Either webhook_url or bot_token must be provided"
            )

        # Validate webhook URL if provided
        if self.webhook_url:
            if not self.webhook_url.startswith("https://discord.com/api/webhooks/"):
                errors.append(
                    f"Invalid webhook URL: must start with 'https://discord.com/api/webhooks/'"
                )

        # Validate bot configuration if bot_token is provided
        if self.bot_token and not self.channel_id:
            errors.append(
                "channel_id is required when using bot_token"
            )

        # Validate retry settings
        if self.max_retries < 0:
            errors.append(
                f"max_retries must be non-negative, got {self.max_retries}"
            )

        if self.retry_delay < 0:
            errors.append(
                f"retry_delay must be non-negative, got {self.retry_delay}"
            )

        if self.timeout <= 0:
            errors.append(
                f"timeout must be positive, got {self.timeout}"
            )

        # Validate message settings
        if self.max_message_length <= 0 or self.max_message_length > 2000:
            errors.append(
                f"max_message_length must be between 1 and 2000, got {self.max_message_length}"
            )

        return len(errors) == 0, errors


@dataclass
class DiscordMessage:
    """Discord message structure."""

    content: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    embeds: Optional[list[dict]] = None
    tts: bool = False

    def validate(self) -> tuple[bool, list[str]]:
        """Validate message content.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.content or not self.content.strip():
            errors.append("Message content cannot be empty")

        if self.embeds:
            if len(self.embeds) > 10:
                errors.append(
                    f"Too many embeds: Discord allows max 10, got {len(self.embeds)}"
                )

        return len(errors) == 0, errors

    def split_content(
        self,
        max_length: int = 2000,
        delimiter: str = "\n"
    ) -> list[str]:
        """Split long content into multiple messages.

        Args:
            max_length: Maximum length per message
            delimiter: Delimiter to use for splitting

        Returns:
            List of message parts
        """
        if len(self.content) <= max_length:
            return [self.content]

        parts = []
        current_part = ""

        # Split by delimiter to preserve structure
        lines = self.content.split(delimiter)

        for line in lines:
            test_part = current_part + delimiter + line if current_part else line

            if len(test_part) <= max_length:
                current_part = test_part
            else:
                # Save current part and start new one
                if current_part:
                    parts.append(current_part)
                # If line itself exceeds max_length, split it by character
                if len(line) > max_length:
                    for i in range(0, len(line), max_length):
                        parts.append(line[i:i + max_length])
                    current_part = ""
                else:
                    current_part = line

        # Add remaining part
        if current_part:
            parts.append(current_part)

        return parts


class DiscordClient:
    """Discord webhook and bot API client."""

    def __init__(self, config: DiscordConfig):
        """Initialize Discord client.

        Args:
            config: Discord configuration

        Raises:
            ValueError: If configuration is invalid
        """
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid Discord configuration: {'; '.join(errors)}")

        self.config = config
        self._client = httpx.Client(timeout=config.timeout)
        logger.info(
            f"Discord client initialized: "
            f"webhook={'yes' if config.webhook_url else 'no'}, "
            f"bot={'yes' if config.bot_token else 'no'}"
        )

    def send_message(
        self,
        message: DiscordMessage,
        message_type: DiscordMessageType = DiscordMessageType.WEBHOOK
    ) -> tuple[bool, Optional[DiscordError]]:
        """Send a message to Discord.

        Args:
            message: Discord message to send
            message_type: Type of message (webhook or bot)

        Returns:
            Tuple of (success, error) where error is None if successful
        """
        # Validate message
        is_valid, errors = message.validate()
        if not is_valid:
            error = DiscordError(
                error_type=DiscordErrorType.INVALID_URL,
                message=f"Invalid message: {'; '.join(errors)}"
            )
            return False, error

        # Determine message type
        if message_type == DiscordMessageType.WEBHOOK:
            return self._send_webhook_message(message)
        else:
            return self._send_bot_message(message)

    def _send_webhook_message(
        self,
        message: DiscordMessage
    ) -> tuple[bool, Optional[DiscordError]]:
        """Send message via webhook.

        Args:
            message: Discord message to send

        Returns:
            Tuple of (success, error)
        """
        if not self.config.webhook_url:
            error = DiscordError(
                error_type=DiscordErrorType.INVALID_URL,
                message="Webhook URL not configured"
            )
            return False, error

        # Check if message is too long and splitting is disabled
        if not self.config.split_long_messages and len(message.content) > self.config.max_message_length:
            error = DiscordError(
                error_type=DiscordErrorType.INVALID_URL,
                message=f"Message too long: {len(message.content)} characters exceeds max {self.config.max_message_length}"
            )
            return False, error

        # Split long messages if enabled
        contents = [message.content]
        if self.config.split_long_messages and len(message.content) > self.config.max_message_length:
            contents = message.split_content(self.config.max_message_length)

        # Send each part
        last_error = None
        for i, content in enumerate(contents):
            # Prepare payload
            payload = {
                "content": content,
                "tts": message.tts,
            }

            # Add username and avatar if specified
            if message.username or self.config.username:
                payload["username"] = message.username or self.config.username

            if message.avatar_url or self.config.avatar_url:
                payload["avatar_url"] = message.avatar_url or self.config.avatar_url

            # Add embeds if provided (only on first message)
            if message.embeds and i == 0:
                payload["embeds"] = message.embeds

            # Send with retry logic
            success, error = self._send_with_retry(
                url=self.config.webhook_url,
                method="POST",
                json=payload
            )

            if not success:
                last_error = error
                logger.error(f"Failed to send webhook message part {i+1}/{len(contents)}: {error}")
                break

        if last_error:
            return False, last_error

        logger.info(f"Successfully sent webhook message ({len(contents)} part(s))")
        return True, None

    def _send_bot_message(
        self,
        message: DiscordMessage
    ) -> tuple[bool, Optional[DiscordError]]:
        """Send message via bot API.

        Args:
            message: Discord message to send

        Returns:
            Tuple of (success, error)
        """
        if not self.config.bot_token or not self.config.channel_id:
            error = DiscordError(
                error_type=DiscordErrorType.INVALID_URL,
                message="Bot token and channel ID required for bot API"
            )
            return False, error

        # Check if message is too long and splitting is disabled
        if not self.config.split_long_messages and len(message.content) > self.config.max_message_length:
            error = DiscordError(
                error_type=DiscordErrorType.INVALID_URL,
                message=f"Message too long: {len(message.content)} characters exceeds max {self.config.max_message_length}"
            )
            return False, error

        # Prepare API URL
        url = f"https://discord.com/api/v10/channels/{self.config.channel_id}/messages"

        # Prepare headers
        headers = {
            "Authorization": f"Bot {self.config.bot_token}",
            "Content-Type": "application/json"
        }

        # Split long messages if enabled
        contents = [message.content]
        if self.config.split_long_messages and len(message.content) > self.config.max_message_length:
            contents = message.split_content(self.config.max_message_length)

        # Send each part
        last_error = None
        for i, content in enumerate(contents):
            # Prepare payload
            payload = {
                "content": content,
                "tts": message.tts,
            }

            # Add embeds if provided (only on first message)
            if message.embeds and i == 0:
                payload["embeds"] = message.embeds

            # Send with retry logic
            success, error = self._send_with_retry(
                url=url,
                method="POST",
                json=payload,
                headers=headers
            )

            if not success:
                last_error = error
                logger.error(f"Failed to send bot message part {i+1}/{len(contents)}: {error}")
                break

        if last_error:
            return False, last_error

        logger.info(f"Successfully sent bot message ({len(contents)} part(s))")
        return True, None

    def _send_with_retry(
        self,
        url: str,
        method: str = "POST",
        **kwargs
    ) -> tuple[bool, Optional[DiscordError]]:
        """Send HTTP request with retry logic.

        Args:
            url: Request URL
            method: HTTP method
            **kwargs: Additional arguments for httpx.request

        Returns:
            Tuple of (success, error)
        """
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._client.request(method, url, **kwargs)

                # Check for rate limiting
                if response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get("Retry-After", self.config.retry_delay))
                    logger.warning(
                        f"Rate limited, waiting {retry_after}s (attempt {attempt + 1}/{self.config.max_retries + 1})"
                    )

                    # If this was the last attempt, return error
                    if attempt == self.config.max_retries:
                        error = DiscordError(
                            error_type=DiscordErrorType.RATE_LIMIT,
                            message=f"Rate limited after {self.config.max_retries} retries",
                            status_code=response.status_code,
                        )
                        return False, error

                    # Wait and retry
                    self._client.wait(retry_after)
                    continue

                # Check for success
                if response.status_code in (200, 201, 204):
                    return True, None

                # Handle other errors
                error = self._parse_error_response(response)
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {error}"
                )
                last_error = error

            except httpx.TimeoutException as e:
                error = DiscordError(
                    error_type=DiscordErrorType.NETWORK_ERROR,
                    message=f"Request timeout: {e}"
                )
                logger.warning(
                    f"Timeout error (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}"
                )
                last_error = error

            except httpx.NetworkError as e:
                error = DiscordError(
                    error_type=DiscordErrorType.NETWORK_ERROR,
                    message=f"Network error: {e}"
                )
                logger.warning(
                    f"Network error (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}"
                )
                last_error = error

            except httpx.HTTPStatusError as e:
                error = self._parse_error_response(e.response)
                logger.warning(
                    f"HTTP status error (attempt {attempt + 1}/{self.config.max_retries + 1}): {error}"
                )
                last_error = error

            except Exception as e:
                error = DiscordError(
                    error_type=DiscordErrorType.UNKNOWN_ERROR,
                    message=f"Unexpected error: {e}"
                )
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return False, error

            # If not the last attempt, wait before retrying
            if attempt < self.config.max_retries:
                import time
                time.sleep(self.config.retry_delay)

        return False, last_error

    def _parse_error_response(
        self,
        response: httpx.Response
    ) -> DiscordError:
        """Parse error response from Discord API.

        Args:
            response: HTTP response

        Returns:
            DiscordError object
        """
        status_code = response.status_code
        response_text = response.text

        # Determine error type based on status code
        if status_code == 401:
            error_type = DiscordErrorType.AUTHENTICATION_ERROR
            message = "Authentication failed: invalid token"
        elif status_code == 403:
            error_type = DiscordErrorType.FORBIDDEN
            message = "Forbidden: insufficient permissions"
        elif status_code == 404:
            error_type = DiscordErrorType.NOT_FOUND
            message = "Not found: resource does not exist"
        elif status_code == 429:
            error_type = DiscordErrorType.RATE_LIMIT
            message = "Rate limit exceeded"
        elif 400 <= status_code < 500:
            error_type = DiscordErrorType.INVALID_URL
            message = f"Client error: {status_code}"
        else:
            error_type = DiscordErrorType.NETWORK_ERROR
            message = f"Server error: {status_code}"

        # Try to extract error message from response body
        try:
            import json
            error_data = response.json()
            if "message" in error_data:
                message = error_data["message"]
        except Exception:
            pass

        return DiscordError(
            error_type=error_type,
            message=message,
            status_code=status_code,
            response_text=response_text
        )

    def close(self):
        """Close the HTTP client."""
        self._client.close()
        logger.info("Discord client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_discord_client(
    webhook_url: Optional[str] = None,
    bot_token: Optional[str] = None,
    channel_id: Optional[str] = None,
    **kwargs
) -> DiscordClient:
    """Create a Discord client with the specified configuration.

    Args:
        webhook_url: Discord webhook URL
        bot_token: Discord bot token
        channel_id: Discord channel ID (required with bot_token)
        **kwargs: Additional configuration options

    Returns:
        DiscordClient instance

    Raises:
        ValueError: If configuration is invalid
    """
    config = DiscordConfig(
        webhook_url=webhook_url,
        bot_token=bot_token,
        channel_id=channel_id,
        **kwargs
    )

    return DiscordClient(config)


def create_discord_message(
    content: str,
    username: Optional[str] = None,
    avatar_url: Optional[str] = None,
    **kwargs
) -> DiscordMessage:
    """Create a Discord message.

    Args:
        content: Message content
        username: Override username (webhook only)
        avatar_url: Override avatar URL (webhook only)
        **kwargs: Additional message options

    Returns:
        DiscordMessage instance
    """
    return DiscordMessage(
        content=content,
        username=username,
        avatar_url=avatar_url,
        **kwargs
    )


# Export public API
__all__ = [
    "DiscordMessageType",
    "DiscordErrorType",
    "DiscordError",
    "DiscordConfig",
    "DiscordMessage",
    "DiscordClient",
    "create_discord_client",
    "create_discord_message",
]
