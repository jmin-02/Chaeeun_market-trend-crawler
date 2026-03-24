"""Weekly scheduler for automatic Discord report transmission.
This module provides a scheduler that automatically generates and sends
weekly Discord reports with crawled tech news articles.

Features:
- Weekly scheduling (configurable day and time)
- Automatic Discord report generation
- Discord webhook and bot API support
- Error handling and retry logic
- Comprehensive logging
- Report aggregation from multiple crawlers
"""

import asyncio
from logging import getLogger

logger = getLogger(__name__)

from base import BaseCrawler
from discord_client import DiscordClient
from discord_formatter import format_full_discord_report
from models import Article, SourceLanguage
from report_categorization import categorize_for_report
from insight_categorization import InsightCategory
from scheduler import ScheduleTask
