"""Weekly scheduler for automatic Discord report transmission.

This module provides a scheduler that automatically generates and sends
weekly Discord reports with crawled tech news articles.

Features:
- Daily crawling at configured times (10 AM, 5 PM)
- Weekly Discord report generation
- Discord bot API support
- Error handling and retry logic
- Report aggregation from multiple crawlers
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta

from .base import BaseCrawler, CrawlerConfig
from .discord_client import DiscordClient, DiscordConfig, DiscordMessage, DiscordMessageType
from .discord_formatter import format_full_discord_report
from .models import Article, SourceLanguage
from .report_categorization import categorize_for_report
from .scheduler import DailyScheduler, ScheduleConfig, ScheduleTask
from .sites import ALL_CRAWLERS
from .sites.korean_sites_config import KOREAN_SITES_CONFIG
from .sites.international_sites_config import INTERNATIONAL_SITES

logger = logging.getLogger(__name__)


def build_tasks() -> list[ScheduleTask]:
    """Build schedule tasks from site configurations."""
    tasks = []

    for site_config in KOREAN_SITES_CONFIG:
        if site_config.enabled:
            tasks.append(ScheduleTask(
                name=site_config.name,
                url=site_config.url,
                source=site_config.name,
                language=site_config.language.value,
                enabled=True,
            ))

    for site_config in INTERNATIONAL_SITES:
        if site_config.enabled:
            tasks.append(ScheduleTask(
                name=site_config.name,
                url=site_config.url,
                source=site_config.name,
                language=site_config.language.value,
                enabled=True,
            ))

    return tasks


def create_discord_client() -> DiscordClient:
    """Create Discord client from environment variables."""
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    channel_id = os.environ.get("DISCORD_CHANNEL_ID")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    config = DiscordConfig(
        bot_token=bot_token,
        channel_id=channel_id,
        webhook_url=webhook_url,
    )

    return DiscordClient(config)


async def run_crawl_cycle(config: CrawlerConfig, tasks: list[ScheduleTask]) -> list[Article]:
    """Run a single crawl cycle using site-specific crawlers."""
    all_articles: list[Article] = []
    semaphore = asyncio.Semaphore(5)

    async def crawl_site(task: ScheduleTask) -> tuple[str, list[Article]]:
        async with semaphore:
            CrawlerClass = ALL_CRAWLERS.get(task.name)
            if not CrawlerClass:
                logger.warning(f"No crawler found for {task.name}, using BaseCrawler")
                CrawlerClass = BaseCrawler

            try:
                async with CrawlerClass(config=config) as crawler:
                    articles = await crawler.crawl(task.url, task.source, task.language)
                    return task.name, articles
            except Exception as e:
                logger.error(f"  {task.name} failed: {e}")
                return task.name, []

    results = await asyncio.gather(*[crawl_site(t) for t in tasks])

    for name, articles in results:
        if articles:
            logger.info(f"  {name}: {len(articles)} articles")
        all_articles.extend(articles)

    logger.info(f"Total articles crawled: {len(all_articles)}")
    return all_articles


async def generate_and_send_report(articles: list[Article], discord: DiscordClient) -> bool:
    """Generate weekly report and send to Discord."""
    if not articles:
        logger.warning("No articles to report")
        return False

    now = datetime.now()
    period_start = now - timedelta(days=7)
    period_end = now

    # Categorize articles for report
    aggregation = categorize_for_report(articles, period_start, period_end)

    # Format as Discord message
    report_text = format_full_discord_report(aggregation, language=SourceLanguage.KOREAN)

    # Send to Discord
    message = DiscordMessage(content=report_text)

    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    msg_type = DiscordMessageType.BOT if bot_token else DiscordMessageType.WEBHOOK

    success, error = discord.send_message(message, message_type=msg_type)

    if success:
        logger.info("Weekly report sent successfully to Discord")
    else:
        logger.error(f"Failed to send report: {error}")

    return success


async def main():
    """Main entry point for the market trend crawler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    logger.info("=== Market Trend Crawler Starting ===")

    # Build tasks from site configs
    tasks = build_tasks()
    logger.info(f"Loaded {len(tasks)} crawling tasks")

    # Create crawler
    config = CrawlerConfig(
        rate_limit=2.0,
        max_retries=3,
        timeout=30,
    )

    # Run crawl cycle with site-specific crawlers
    articles = await run_crawl_cycle(config, tasks)

    # Create Discord client and send report
    try:
        discord = create_discord_client()
        await generate_and_send_report(articles, discord)
        discord.close()
    except ValueError as e:
        logger.error(f"Discord client configuration error: {e}")
        logger.info("Skipping Discord report. Set DISCORD_BOT_TOKEN or DISCORD_WEBHOOK_URL in .env")

    logger.info("=== Market Trend Crawler Complete ===")
