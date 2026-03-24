# Weekly Scheduler Guide

> Automatic Discord report transmission scheduler

## Overview

The `WeeklyScheduler` provides automated weekly report generation and Discord transmission for tech news articles crawled from 30+ sites. It integrates crawling, report generation, and Discord sending into a single, automated workflow.

### Key Features

- **Weekly Scheduling**: Configurable day and time for automatic reports
- **Automatic Crawling**: Runs all registered crawler tasks
- **Report Generation**: Creates Discord-formatted reports with category grouping
- **Discord Integration**: Supports both webhook and bot API methods
- **Error Handling**: Graceful error handling and retry logic
- **Multiple Channels**: Send to multiple Discord channels
- **Statistics**: Comprehensive logging and monitoring
- **Bilingual Support**: Korean and English reports

## Installation

The weekly scheduler is part of the Ouroboros crawler framework:

```python
from ouroboros.crawler import (
    WeeklyScheduler,
    WeeklySchedulerConfig,
    WeeklyReportTask,
    ScheduleTask,
)
```

## Quick Start

### Basic Usage

```python
import asyncio
from datetime import time
from ouroboros.crawler import (
    WeeklyScheduler,
    WeeklySchedulerConfig,
    ScheduleTask,
    WeeklyReportTask,
    SourceLanguage,
)

async def main():
    # Step 1: Create scheduler configuration
    config = WeeklySchedulerConfig(
        day_of_week=4,  # Friday (0=Monday, 6=Sunday)
        send_time=time(10, 0),  # 10 AM
        discord_webhook_url="https://discord.com/api/webhooks/ID/TOKEN",
        report_period_days=7,  # Last 7 days
        report_language=SourceLanguage.ENGLISH,
    )

    # Step 2: Create scheduler
    scheduler = WeeklyScheduler(config=config)

    # Step 3: Register crawler tasks
    scheduler.register_crawl_tasks([
        ScheduleTask(
            name="TechCrunch",
            url="https://techcrunch.com",
            source="TechCrunch",
            language="en",
        ),
        ScheduleTask(
            name="Bloter",
            url="https://www.bloter.net",
            source="Bloter",
            language="ko",
        ),
    ])

    # Step 4: Register report tasks
    scheduler.register_report_tasks([
        WeeklyReportTask(name="Main Weekly Report"),
    ])

    # Step 5: Run immediate report cycle (for testing)
    await scheduler.run_once()

    # Or start automatic weekly scheduler
    # await scheduler.start()

asyncio.run(main())
```

### Background Scheduler

```python
async def run_background_scheduler():
    scheduler = WeeklyScheduler(config=config)

    # Register tasks...
    scheduler.register_crawl_tasks([...])
    scheduler.register_report_tasks([...])

    try:
        # Start automatic weekly scheduler
        await scheduler.start()
    except KeyboardInterrupt:
        # Graceful shutdown
        await scheduler.stop()
```

## Configuration

### WeeklySchedulerConfig

Configuration for weekly Discord report scheduler.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `day_of_week` | int | 4 | Day to send reports (0=Monday, 6=Sunday) |
| `send_time` | time | 10:00 | Time to send reports |
| `discord_webhook_url` | str | None | Discord webhook URL |
| `discord_bot_token` | str | None | Discord bot token |
| `discord_channel_id` | str | None | Discord channel ID (for bot API) |
| `report_period_days` | int | 7 | Number of days to include in report |
| `report_language` | SourceLanguage | ENGLISH | Language for reports |
| `discord_username` | str | "Tech News Weekly" | Custom Discord username |
| `discord_avatar_url` | str | None | Custom Discord avatar URL |

### Discord Credentials

The scheduler supports two methods of Discord integration:

#### Method 1: Webhook (Recommended)

```python
config = WeeklySchedulerConfig(
    day_of_week=4,
    send_time=time(10, 0),
    discord_webhook_url="https://discord.com/api/webhooks/ID/TOKEN",
)
```

**Advantages**:
- Simple setup
- No bot permissions needed
- Lower rate limits

#### Method 2: Bot API

```python
config = WeeklySchedulerConfig(
    day_of_week=4,
    send_time=time(10, 0),
    discord_bot_token="YOUR_BOT_TOKEN",
    discord_channel_id="123456789",
)
```

**Advantages**:
- Full Discord API access
- Can send to multiple channels
- More features

## Task Management

### Crawler Tasks

Crawler tasks define which sites to crawl and how.

```python
# Single task
task = ScheduleTask(
    name="TechCrunch",
    url="https://techcrunch.com",
    source="TechCrunch",
    language="en",
    enabled=True,
)
scheduler.register_crawl_task(task)

# Multiple tasks
tasks = [
    ScheduleTask(name="Site 1", url="https://site1.com", source="Source 1", language="en"),
    ScheduleTask(name="Site 2", url="https://site2.com", source="Source 2", language="en"),
]
scheduler.register_crawl_tasks(tasks)
```

### Report Tasks

Report tasks define which Discord channels to send reports to.

```python
# Single task
task = WeeklyReportTask(
    name="Main Channel",
    enabled=True,
    last_sent_at=None,
)
scheduler.register_report_task(task)

# Multiple tasks (different channels)
tasks = [
    WeeklyReportTask(name="General Channel"),
    WeeklyReportTask(name="AI/ML Channel"),
    WeeklyReportTask(name="Weekly Digest"),
]
scheduler.register_report_tasks(tasks)
```

## Scheduler Lifecycle

### Starting the Scheduler

```python
# Start automatic weekly scheduler
await scheduler.start()
```

The scheduler will:
1. Calculate next scheduled run time
2. Wait until that time
3. Run all crawler tasks
4. Generate Discord report
5. Send to all enabled report tasks
6. Repeat weekly

### Running Once

```python
# Run a single report cycle immediately (for testing)
success = await scheduler.run_once()
```

### Stopping the Scheduler

```python
# Stop gracefully
await scheduler.stop()
```

## Error Handling

The scheduler handles errors gracefully:

### Crawler Errors

```python
# Individual crawler task failures don't stop the cycle
# Failed tasks are logged, successful results are used
```

### Discord Send Errors

```python
# Failed Discord sends are logged
# The scheduler will retry next week
# Report task.last_sent_at is only updated on success
```

### Exception Handling

```python
try:
    await scheduler.start()
except Exception as e:
    logger.error(f"Scheduler error: {e}")
    await scheduler.stop()
```

## Statistics and Monitoring

### Getting Statistics

```python
stats = scheduler.get_stats()

print(stats)
# {
#     "scheduler": {
#         "type": "weekly",
#         "day_of_week": 4,
#         "send_time": "10:00",
#         "running": False,
#         "total_report_tasks": 3,
#         "enabled_report_tasks": 2,
#         "total_crawl_tasks": 10,
#         "enabled_crawl_tasks": 8,
#         "report_period_days": 7,
#         "report_language": "en",
#     },
#     "crawler": {
#         "session_id": "abc12345-...",
#         "requests": {
#             "total": 100,
#             "successful": 95,
#             "failed": 5,
#             "success_rate": 0.95
#         },
#         ...
#     }
# }
```

### Logging

The scheduler provides comprehensive logging:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Scheduler logs:
# - Scheduled run times
# - Crawler task execution
# - Article collection results
# - Report generation
# - Discord send results
# - Errors and warnings
```

## Advanced Usage

### Custom Report Period

```python
# Include last 5 days instead of 7
config = WeeklySchedulerConfig(
    day_of_week=4,
    send_time=time(10, 0),
    report_period_days=5,  # Custom period
)
```

### Bilingual Reports

```python
# Korean reports
config = WeeklySchedulerConfig(
    day_of_week=4,
    send_time=time(10, 0),
    report_language=SourceLanguage.KOREAN,
    discord_username="주간 테크 뉴스",
)
```

### Multiple Discord Channels

```python
# Send same report to multiple channels
scheduler.register_report_tasks([
    WeeklyReportTask(name="#general"),
    WeeklyReportTask(name="#ai-ml"),
    WeeklyReportTask(name="#weekly-digest"),
])
```

### Custom Schedule

```python
# Monday 9 AM
config = WeeklySchedulerConfig(
    day_of_week=0,  # Monday
    send_time=time(9, 0),
)

# Sunday 6 PM
config = WeeklySchedulerConfig(
    day_of_week=6,  # Sunday
    send_time=time(18, 0),
)
```

## Integration with Existing Systems

### With AC1 (Crawling)

```python
# The scheduler uses existing crawler infrastructure
crawler = BaseCrawler()
scheduler = WeeklyScheduler(config=config, crawler=crawler)
```

### With AC2 (Classification)

```python
# Articles are automatically classified
# Reports are grouped by 5 categories
# Category statistics included in reports
```

### With AC3 (Discord Formatting)

```python
# Reports use Discord formatter
# Markdown-safe formatting
# Emoji-enhanced presentation
# Category-grouped display
```

### With AC4 (Job Seeker Insights)

```python
# Insight categories integrated
# Job seeker-focused sections
# Skills, companies, salaries extracted
```

## Best Practices

### 1. Environment Variables

Store Discord credentials in environment variables:

```bash
export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/ID/TOKEN'
```

```python
import os

config = WeeklySchedulerConfig(
    discord_webhook_url=os.environ.get("DISCORD_WEBHOOK_URL"),
)
```

### 2. Graceful Shutdown

Always stop the scheduler gracefully:

```python
import signal

def signal_handler(signum, frame):
    asyncio.create_task(scheduler.stop())

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 3. Error Monitoring

Monitor errors and set up alerts:

```python
import logging

logger = logging.getLogger(__name__)

# Check stats periodically
stats = scheduler.get_stats()
if stats["crawler"]["requests"]["success_rate"] < 0.9:
    logger.warning(f"Low success rate: {stats}")
```

### 4. Resource Management

Use context managers where possible:

```python
# The scheduler manages resources automatically
# Discord client is created and closed properly
# Crawler sessions are cleaned up
```

## Troubleshooting

### Common Issues

#### 1. Scheduler Not Running

**Problem**: Scheduler doesn't start

**Solution**: Check configuration
```python
config = WeeklySchedulerConfig(
    discord_webhook_url="URL",  # Must be provided
)
```

#### 2. No Articles Crawled

**Problem**: Report has no articles

**Solution**: Check crawler tasks
```python
# Ensure tasks are enabled
task = ScheduleTask(..., enabled=True)
scheduler.register_crawl_task(task)
```

#### 3. Discord Send Fails

**Problem**: Reports not sent to Discord

**Solution**: Check credentials
```bash
# Test webhook URL
curl -X POST "https://discord.com/api/webhooks/ID/TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'
```

#### 4. Old Articles in Report

**Problem**: Report includes old articles

**Solution**: Check report period
```python
config = WeeklySchedulerConfig(
    report_period_days=7,  # Last 7 days only
)
```

## Performance Considerations

### Scalability

- **Sites**: No limit (tested with 30+ sites)
- **Articles**: Efficient handling of large datasets
- **Channels**: Multiple Discord channels supported
- **Memory**: Minimal footprint

### Concurrency

- **Crawler Tasks**: Max 5 concurrent (configurable)
- **Report Tasks**: Sequential (to avoid rate limits)
- **Discord Sends**: Respect rate limits automatically

## Security Considerations

### Credential Management

1. **Environment Variables**: Store in environment, not code
2. **Secrets Management**: Use secrets manager in production
3. **Access Control**: Limit Discord webhook permissions
4. **Logging**: Don't log sensitive credentials

### Code Example

```python
import os

# Good: Read from environment
webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

# Bad: Hardcode credentials
webhook_url = "https://discord.com/api/webhooks/ID/TOKEN"
```

## Testing

### Unit Tests

```bash
pytest tests/unit/crawler/test_weekly_scheduler.py -v
```

### Integration Tests

```python
# Run example
python examples/weekly_report_scheduler_example.py
```

### Mocking

```python
from unittest.mock import AsyncMock

# Mock Discord client
scheduler._discord_client = AsyncMock()
scheduler._discord_client.send_message = AsyncMock(return_value=(True, None))
```

## API Reference

### WeeklyScheduler

Main scheduler class.

#### Methods

- `register_crawl_task(task: ScheduleTask) -> None`
- `register_crawl_tasks(tasks: list[ScheduleTask]) -> None`
- `register_report_task(task: WeeklyReportTask) -> None`
- `register_report_tasks(tasks: list[WeeklyReportTask]) -> None`
- `start() -> Awaitable[None]`
- `stop() -> Awaitable[None]`
- `run_once() -> Awaitable[bool]`
- `get_stats() -> dict`

#### Attributes

- `config: WeeklySchedulerConfig`
- `crawler: BaseCrawler`
- `tasks: list[WeeklyReportTask]`
- `crawl_tasks: list[ScheduleTask]`
- `_running: bool`

### WeeklySchedulerConfig

Configuration dataclass.

#### Fields

- `day_of_week: int` (0-6)
- `send_time: time`
- `discord_webhook_url: Optional[str]`
- `discord_bot_token: Optional[str]`
- `discord_channel_id: Optional[str]`
- `report_period_days: int`
- `report_language: SourceLanguage`
- `discord_username: Optional[str]`
- `discord_avatar_url: Optional[str]`

### WeeklyReportTask

Report task model.

#### Fields

- `name: str`
- `enabled: bool`
- `last_sent_at: Optional[datetime]`

## Examples

See `examples/weekly_report_scheduler_example.py` for complete working examples.

## License

Part of the Ouroboros AI Workflow System project.
