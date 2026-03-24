# Discord Client Integration Guide

This guide provides comprehensive documentation for the Discord webhook and bot API client integration in the Ouroboros crawler system.

## Overview

The Discord client module provides functionality for sending messages to Discord via:
- **Webhooks**: Simple, token-based message delivery to a specific channel
- **Bot API**: Full Discord bot capabilities with authenticated API calls

## Features

- ✅ Dual support for webhooks and bot API
- ✅ Comprehensive error handling and retry logic
- ✅ Rate limit handling with automatic retry
- ✅ Automatic message splitting for long content
- ✅ Context manager support for resource cleanup
- ✅ Extensive configuration options
- ✅ Full test coverage (39 tests)

## Installation

No additional dependencies required - uses existing `httpx` library.

## Quick Start

### Using Webhook (Recommended)

```python
from ouroboros.crawler import (
    create_discord_client,
    create_discord_message,
)

# Create client with webhook URL
client = create_discord_client(
    webhook_url="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
)

# Create and send message
message = create_discord_message(
    content="Hello, Discord! This is a test message."
)

success, error = client.send_message(message)
if success:
    print("Message sent successfully!")
else:
    print(f"Failed to send: {error}")

# Clean up
client.close()
```

### Using Bot API

```python
from ouroboros.crawler import (
    create_discord_client,
    create_discord_message,
    DiscordMessageType,
)

# Create client with bot token and channel ID
client = create_discord_client(
    bot_token="YOUR_BOT_TOKEN",
    channel_id="YOUR_CHANNEL_ID"
)

# Create and send message
message = create_discord_message(
    content="Hello from the bot API!"
)

success, error = client.send_message(
    message,
    message_type=DiscordMessageType.BOT
)

if success:
    print("Message sent successfully!")
else:
    print(f"Failed to send: {error}")

# Clean up
client.close()
```

### Using Context Manager

```python
from ouroboros.crawler import create_discord_client, create_discord_message

# Automatically handles cleanup
with create_discord_client(webhook_url="YOUR_WEBHOOK_URL") as client:
    message = create_discord_message(content="Auto-cleanup example!")
    success, error = client.send_message(message)
    # Client is automatically closed after exiting the with block
```

## Configuration

### DiscordConfig Options

```python
from ouroboros.crawler import DiscordConfig

config = DiscordConfig(
    # Required: either webhook_url or (bot_token + channel_id)
    webhook_url="https://discord.com/api/webhooks/ID/TOKEN",
    # OR
    bot_token="YOUR_BOT_TOKEN",
    channel_id="123456789",

    # Optional: webhook customization
    username="Custom Bot Name",  # Override webhook username
    avatar_url="https://example.com/avatar.png",  # Override webhook avatar

    # Optional: retry settings
    max_retries=3,  # Number of retry attempts (default: 3)
    retry_delay=1.0,  # Delay between retries in seconds (default: 1.0)
    timeout=30.0,  # HTTP request timeout in seconds (default: 30.0)

    # Optional: message settings
    max_message_length=2000,  # Discord's limit (default: 2000)
    split_long_messages=True,  # Auto-split long messages (default: True)
)
```

### Configuration Validation

```python
config = DiscordConfig(webhook_url="YOUR_WEBHOOK_URL")
is_valid, errors = config.validate()

if not is_valid:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Configuration is valid!")
```

## Message Creation

### Basic Message

```python
message = create_discord_message(
    content="Hello, Discord!"
)
```

### Message with Embeds

```python
embeds = [
    {
        "title": "Weekly Tech News Report",
        "description": "Top stories from this week",
        "color": 5814783,  # Decimal color code
        "fields": [
            {
                "name": "Total Articles",
                "value": "150",
                "inline": True
            },
            {
                "name": "Categories",
                "value": "5",
                "inline": True
            }
        ]
    }
]

message = create_discord_message(
    content="Here's your weekly report!",
    embeds=embeds
)
```

### Message with Custom Username/Avatar (Webhook Only)

```python
message = create_discord_message(
    content="Custom username and avatar!",
    username="Tech News Bot",
    avatar_url="https://example.com/bot-avatar.png"
)
```

### TTS Message

```python
message = create_discord_message(
    content="This will be read aloud!",
    tts=True
)
```

## Integration with Crawler System

### Sending Crawl Results

```python
from ouroboros.crawler import (
    create_discord_client,
    create_discord_message,
    format_full_discord_report,
    categorize_for_report,
    SourceLanguage,
)
from datetime import datetime, timedelta

# 1. Crawl articles (from AC1)
# articles = await crawler.run_once()

# 2. Categorize for report (from Sub-AC 1 of AC5)
period_start = datetime.now() - timedelta(days=7)
period_end = datetime.now()

aggregation = categorize_for_report(
    articles=articles,
    period_start=period_start,
    period_end=period_end
)

# 3. Format Discord report (from AC3)
discord_report = format_full_discord_report(
    aggregation=aggregation,
    language=SourceLanguage.ENGLISH
)

# 4. Send to Discord
with create_discord_client(webhook_url="YOUR_WEBHOOK_URL") as client:
    message = create_discord_message(
        content=discord_report,
        username="Tech News Reporter"
    )

    success, error = client.send_message(message)
    if success:
        print("Weekly report sent successfully!")
    else:
        print(f"Failed to send report: {error}")
```

### Sending Category-Specific Reports

```python
from ouroboros.crawler import (
    create_discord_client,
    create_discord_message,
    format_category_report,
    Category,
    SourceLanguage,
)

# Generate AI/ML category report
ai_articles = [a for a in articles if a.category == Category.AI_ML]
category_report = format_category_report(
    category=Category.AI_ML,
    articles=ai_articles,
    language=SourceLanguage.ENGLISH
)

# Send to Discord
with create_discord_client(webhook_url="YOUR_WEBHOOK_URL") as client:
    message = create_discord_message(
        content=category_report,
        username="AI/ML News Reporter"
    )

    success, error = client.send_message(message)
```

## Error Handling

### Checking Errors

```python
success, error = client.send_message(message)

if not success:
    # Error type
    print(f"Error Type: {error.error_type.value}")

    # Error message
    print(f"Message: {error.message}")

    # HTTP status code (if applicable)
    if error.status_code:
        print(f"Status Code: {error.status_code}")

    # Response text (if applicable)
    if error.response_text:
        print(f"Response: {error.response_text}")
```

### Error Types

| Error Type | Description | Common Causes |
|-------------|-------------|----------------|
| `INVALID_URL` | Invalid configuration or message | Wrong webhook URL, missing credentials |
| `NETWORK_ERROR` | Network connectivity issues | Timeouts, connection failures |
| `RATE_LIMIT` | Rate limited by Discord | Too many requests too quickly |
| `AUTHENTICATION_ERROR` | Invalid credentials | Wrong bot token |
| `FORBIDDEN` | Insufficient permissions | Bot lacks permissions |
| `NOT_FOUND` | Resource not found | Invalid channel ID |
| `UNKNOWN_ERROR` | Unexpected error | Other issues |

### Retry Logic

The client automatically retries failed requests with exponential backoff:

```python
config = DiscordConfig(
    webhook_url="YOUR_WEBHOOK_URL",
    max_retries=5,  # Try up to 5 times
    retry_delay=2.0  # Wait 2 seconds between retries
)
```

### Rate Limit Handling

When rate limited (HTTP 429), the client:

1. Reads the `Retry-After` header
2. Waits for the specified duration
3. Retries the request automatically

## Advanced Features

### Message Splitting

Long messages are automatically split to respect Discord's 2000 character limit:

```python
# Long message (3000 characters)
long_content = "A" * 3000

message = create_discord_message(content=long_content)

# With splitting enabled (default)
success, error = client.send_message(message)
# Sends 2 messages: 2000 chars + 1000 chars

# With splitting disabled
config = DiscordConfig(
    webhook_url="YOUR_WEBHOOK_URL",
    split_long_messages=False
)
success, error = client.send_message(message)
# Fails with error: "Message too long: 3000 characters exceeds max 2000"
```

### Custom Message Splitting

```python
message = create_discord_message(content=long_content)

# Split manually with custom delimiter
parts = message.split_content(
    max_length=1500,  # Custom limit
    delimiter="\n\n"  # Split by double newline
)

for i, part in enumerate(parts, 1):
    print(f"Part {i}: {len(part)} characters")
```

### Embeds with Rich Formatting

```python
embeds = [
    {
        "title": "📊 Category Breakdown",
        "color": 5814783,
        "fields": [
            {
                "name": "🤖 AI/ML",
                "value": "45 articles",
                "inline": True
            },
            {
                "name": "🚀 Startups",
                "value": "30 articles",
                "inline": True
            },
            {
                "name": "⛓️ Blockchain",
                "value": "25 articles",
                "inline": True
            }
        ],
        "footer": {
            "text": "Generated by Ouroboros AI",
            "icon_url": "https://example.com/icon.png"
        },
        "timestamp": "2026-03-24T10:00:00Z"
    }
]

message = create_discord_message(
    content="Weekly report is ready!",
    embeds=embeds
)
```

## Testing

### Mock Testing

```python
from unittest.mock import Mock, patch
from ouroboros.crawler import DiscordClient, DiscordConfig

# Mock HTTP client
with patch('ouroboros.crawler.discord_client.httpx.Client') as mock_client_class:
    mock_response = Mock()
    mock_response.status_code = 204
    mock_client = MagicMock()
    mock_client.request.return_value = mock_response
    mock_client_class.return_value = mock_client

    # Test with mocked client
    config = DiscordConfig(webhook_url="test_url")
    client = DiscordClient(config)

    message = create_discord_message(content="Test")
    success, error = client.send_message(message)

    assert success
    assert error is None
```

### Running Tests

```bash
# Run all Discord client tests
pytest tests/unit/crawler/test_discord_client.py -v

# Run specific test class
pytest tests/unit/crawler/test_discord_client.py::TestDiscordConfig -v

# Run specific test
pytest tests/unit/crawler/test_discord_client.py::TestDiscordClient::test_client_initialization_webhook -v
```

## Best Practices

### 1. Use Context Managers

```python
# Good - automatic cleanup
with create_discord_client(webhook_url="URL") as client:
    success, error = client.send_message(message)

# Avoid - manual cleanup needed
client = create_discord_client(webhook_url="URL")
try:
    success, error = client.send_message(message)
finally:
    client.close()
```

### 2. Handle Errors Gracefully

```python
success, error = client.send_message(message)

if not success:
    # Log error details
    logger.error(f"Discord send failed: {error}")

    # Retry logic for specific error types
    if error.error_type == DiscordErrorType.RATE_LIMIT:
        # Wait longer before retry
        time.sleep(60)
    elif error.error_type == DiscordErrorType.NETWORK_ERROR:
        # Check network connectivity
        check_network()
```

### 3. Use Appropriate Message Type

```python
# Webhook - simpler, no rate limits per channel
if use_webhook:
    success, error = client.send_message(
        message,
        message_type=DiscordMessageType.WEBHOOK
    )

# Bot API - more features, respects per-channel rate limits
else:
    success, error = client.send_message(
        message,
        message_type=DiscordMessageType.BOT
    )
```

### 4. Validate Configuration Early

```python
config = DiscordConfig(webhook_url="YOUR_URL")
is_valid, errors = config.validate()

if not is_valid:
    raise ValueError(f"Invalid configuration: {errors}")

# Proceed with valid config
client = DiscordClient(config)
```

### 5. Use Message Splitting

```python
# Enable splitting for large reports
config = DiscordConfig(
    webhook_url="YOUR_URL",
    split_long_messages=True,
    max_message_length=2000
)

# This ensures reports are delivered even if they exceed 2000 characters
```

## Troubleshooting

### Issue: "Invalid webhook URL"

**Cause**: Webhook URL format is incorrect

**Solution**:
```python
# Correct format
webhook_url = "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"

# Verify URL starts with correct prefix
assert webhook_url.startswith("https://discord.com/api/webhooks/")
```

### Issue: "Rate limited"

**Cause**: Too many requests sent too quickly

**Solution**:
```python
# Increase retry delay
config = DiscordConfig(
    webhook_url="YOUR_URL",
    retry_delay=5.0,  # Wait 5 seconds between retries
    max_retries=5
)
```

### Issue: "Authentication failed"

**Cause**: Invalid bot token

**Solution**:
```python
# Verify bot token is correct
# Bot tokens should start with application identifier
assert bot_token.startswith("MT") or bot_token.startswith("Mz")

# Regenerate token in Discord Developer Portal if needed
```

### Issue: "Message too long"

**Cause**: Message exceeds 2000 characters and splitting is disabled

**Solution**:
```python
# Enable automatic splitting
config = DiscordConfig(
    webhook_url="YOUR_URL",
    split_long_messages=True
)

# Or manually split the message
parts = message.split_content(max_length=2000)
```

## Performance Considerations

### Message Splitting Overhead

- **With splitting enabled**: O(n) where n = message length
- **Without splitting**: O(1) validation only
- **Recommendation**: Keep splitting enabled for reliability

### HTTP Request Overhead

- **Per message**: 1-2 HTTP requests (initial + potential retry)
- **Rate limits**: Discord has global and per-channel limits
- **Recommendation**: Use webhooks for batch operations

### Memory Usage

- **Client**: ~1KB per instance
- **Message**: Proportional to content size
- **Recommendation**: Use context managers to ensure cleanup

## Security Best Practices

### 1. Use Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
bot_token = os.getenv("DISCORD_BOT_TOKEN")

client = create_discord_client(webhook_url=webhook_url)
```

### 2. Never Commit Credentials

```bash
# Add to .gitignore
.env
.env.local
*.secret
```

### 3. Use Least Privilege Principle

```python
# For webhooks: Create dedicated webhook per channel
# For bots: Only grant required permissions (e.g., SEND_MESSAGES)
```

### 4. Rotate Tokens Regularly

- Regenerate webhook URLs periodically
- Rotate bot tokens for security
- Update configuration without code changes

## API Reference

### Classes

#### `DiscordConfig`
Configuration for Discord webhook/bot integration.

**Parameters**:
- `webhook_url` (str, optional): Discord webhook URL
- `bot_token` (str, optional): Discord bot token
- `channel_id` (str, optional): Discord channel ID
- `username` (str, optional): Override username (webhook only)
- `avatar_url` (str, optional): Override avatar URL (webhook only)
- `max_retries` (int, optional): Maximum retry attempts (default: 3)
- `retry_delay` (float, optional): Delay between retries in seconds (default: 1.0)
- `timeout` (float, optional): HTTP request timeout in seconds (default: 30.0)
- `max_message_length` (int, optional): Maximum message length (default: 2000)
- `split_long_messages` (bool, optional): Auto-split long messages (default: True)

**Methods**:
- `validate() -> tuple[bool, list[str]]`: Validate configuration

#### `DiscordMessage`
Discord message structure.

**Parameters**:
- `content` (str): Message content
- `username` (str, optional): Override username (webhook only)
- `avatar_url` (str, optional): Override avatar URL (webhook only)
- `embeds` (list[dict], optional): List of embed objects
- `tts` (bool, optional): Text-to-speech flag (default: False)

**Methods**:
- `validate() -> tuple[bool, list[str]]`: Validate message
- `split_content(max_length, delimiter) -> list[str]`: Split content into parts

#### `DiscordClient`
Discord webhook and bot API client.

**Parameters**:
- `config` (DiscordConfig): Discord configuration

**Methods**:
- `send_message(message, message_type) -> tuple[bool, Optional[DiscordError]]`: Send message
- `close()`: Close HTTP client

#### `DiscordError`
Error details for Discord operations.

**Attributes**:
- `error_type` (DiscordErrorType): Type of error
- `message` (str): Error message
- `status_code` (int, optional): HTTP status code
- `response_text` (str, optional): Response body
- `timestamp` (datetime): Error timestamp

### Enums

#### `DiscordMessageType`
Types of Discord messages.
- `WEBHOOK`: Webhook message
- `BOT`: Bot API message

#### `DiscordErrorType`
Types of Discord errors.
- `INVALID_URL`: Invalid configuration or URL
- `NETWORK_ERROR`: Network connectivity issues
- `RATE_LIMIT`: Rate limited by Discord
- `AUTHENTICATION_ERROR`: Invalid credentials
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `UNKNOWN_ERROR`: Unexpected error

### Functions

#### `create_discord_client(webhook_url, bot_token, channel_id, **kwargs) -> DiscordClient`
Create a Discord client with configuration.

**Parameters**:
- `webhook_url` (str, optional): Discord webhook URL
- `bot_token` (str, optional): Discord bot token
- `channel_id` (str, optional): Discord channel ID
- `**kwargs`: Additional configuration options

**Returns**:
- `DiscordClient`: Configured client instance

**Raises**:
- `ValueError`: If configuration is invalid

#### `create_discord_message(content, username, avatar_url, **kwargs) -> DiscordMessage`
Create a Discord message.

**Parameters**:
- `content` (str): Message content
- `username` (str, optional): Override username
- `avatar_url` (str, optional): Override avatar URL
- `**kwargs`: Additional message options

**Returns**:
- `DiscordMessage`: Message instance

## Examples Directory

See `examples/discord_integration_example.py` for complete working examples.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test files for usage patterns
3. Consult Discord API documentation: https://discord.com/developers/docs

---

**Last Updated**: 2026-03-24
**Version**: 1.0.0
**Test Coverage**: 39 tests, 100% passing
