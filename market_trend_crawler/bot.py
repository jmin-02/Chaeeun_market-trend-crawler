"""Discord bot with slash commands and scheduled crawling.

Slash commands:
  /crawl   — Trigger immediate crawl of all sites
  /report  — Generate and post the weekly report
  /status  — Show bot status and last crawl info
  /sites   — List all configured crawling sites
"""

import asyncio
import logging
import os
from datetime import datetime, time, timedelta, timezone
from typing import Optional

import discord
from discord import app_commands
from discord.ext import tasks

from .base import BaseCrawler, CrawlerConfig
from .discord_formatter import format_full_discord_report
from .models import Article, SourceLanguage
from .report_categorization import categorize_for_report
from .scheduler import DailyScheduler, ScheduleTask
from .sites import ALL_CRAWLERS
from .sites.korean_sites_config import KOREAN_SITES_CONFIG
from .sites.international_sites_config import INTERNATIONAL_SITES

logger = logging.getLogger(__name__)

# KST schedule times (converted to UTC for discord.ext.tasks)
# 10:00 KST = 01:00 UTC, 17:00 KST = 08:00 UTC
CRAWL_TIMES_UTC = [
    time(1, 0, tzinfo=timezone.utc),
    time(8, 0, tzinfo=timezone.utc),
]


def build_tasks() -> list[ScheduleTask]:
    """Build schedule tasks from all site configurations."""
    task_list = []

    for site_config in KOREAN_SITES_CONFIG:
        if site_config.enabled:
            task_list.append(ScheduleTask(
                name=site_config.name,
                url=site_config.url,
                source=site_config.name,
                language=site_config.language.value,
            ))

    for site_config in INTERNATIONAL_SITES:
        if site_config.enabled:
            task_list.append(ScheduleTask(
                name=site_config.name,
                url=site_config.url,
                source=site_config.name,
                language=site_config.language.value,
            ))

    return task_list


class CrawlerBot(discord.Client):
    """Discord bot that crawls tech news and responds to slash commands."""

    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)
        self.crawler_config = CrawlerConfig(
            rate_limit=2.0,
            max_retries=3,
            timeout=30,
        )
        self.crawl_tasks = build_tasks()
        self.last_crawl_time: Optional[datetime] = None
        self.last_article_count: int = 0
        self.cached_articles: list[Article] = []
        self._crawling = False

    async def setup_hook(self):
        """Called when bot is ready. Register commands and start scheduler."""
        guild_id = os.environ.get("DISCORD_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Slash commands synced to guild {guild_id}")
        else:
            await self.tree.sync()
            logger.info("Slash commands synced globally")

        # Start scheduled crawling
        if not self.scheduled_crawl.is_running():
            self.scheduled_crawl.start()

    async def on_ready(self):
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Configured {len(self.crawl_tasks)} crawling tasks")

    async def do_crawl(self) -> list[Article]:
        """Execute a crawl cycle."""
        if self._crawling:
            logger.warning("Crawl already in progress, skipping")
            return self.cached_articles

        self._crawling = True
        try:
            semaphore = asyncio.Semaphore(5)

            async def crawl_site(task):
                async with semaphore:
                    CrawlerClass = ALL_CRAWLERS.get(task.name, BaseCrawler)
                    try:
                        async with CrawlerClass(config=self.crawler_config) as crawler:
                            articles = await crawler.crawl(task.url, task.source, task.language)
                            return task.name, articles
                    except Exception as e:
                        logger.error(f"  {task.name} failed: {e}")
                        return task.name, []

            results = await asyncio.gather(*[crawl_site(t) for t in self.crawl_tasks])

            all_articles = []
            for task_name, articles in results:
                all_articles.extend(articles)
                if articles:
                    logger.info(f"  {task_name}: {len(articles)} articles")

            self.cached_articles = all_articles
            self.last_crawl_time = datetime.now()
            self.last_article_count = len(all_articles)

            logger.info(f"Crawl complete: {len(all_articles)} total articles")
            return all_articles

        finally:
            self._crawling = False

    def generate_report(self, articles: list[Article]) -> str:
        """Generate formatted report from articles."""
        now = datetime.now()
        period_start = now - timedelta(days=7)

        aggregation = categorize_for_report(articles, period_start, now)
        return format_full_discord_report(aggregation, language=SourceLanguage.KOREAN)

    @tasks.loop(time=CRAWL_TIMES_UTC)
    async def scheduled_crawl(self):
        """Scheduled crawl at 10:00 and 17:00 KST."""
        logger.info("=== Scheduled crawl starting ===")
        try:
            articles = await self.do_crawl()

            channel_id = os.environ.get("DISCORD_CHANNEL_ID")
            if channel_id and articles:
                channel = self.get_channel(int(channel_id))
                if channel:
                    report = self.generate_report(articles)
                    # Split if too long for Discord (2000 char limit)
                    for chunk in _split_message(report):
                        await channel.send(chunk)
                    logger.info("Scheduled report sent to channel")
                else:
                    logger.error(f"Channel {channel_id} not found")
        except Exception as e:
            logger.error(f"Scheduled crawl failed: {e}", exc_info=True)

    @scheduled_crawl.before_loop
    async def before_scheduled_crawl(self):
        await self.wait_until_ready()


def _split_message(text: str, limit: int = 2000) -> list[str]:
    """Split message into chunks respecting Discord's character limit."""
    if len(text) <= limit:
        return [text]

    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > limit:
            if current:
                chunks.append(current)
            # Handle single lines exceeding limit
            if len(line) > limit:
                for i in range(0, len(line), limit):
                    chunks.append(line[i:i + limit])
                current = ""
            else:
                current = line
        else:
            current = current + "\n" + line if current else line

    if current:
        chunks.append(current)

    return chunks


def create_bot() -> CrawlerBot:
    """Create and configure the bot with slash commands."""
    bot = CrawlerBot()

    @bot.tree.command(name="crawl", description="지금 바로 크롤링을 실행합니다")
    async def cmd_crawl(interaction: discord.Interaction):
        if bot._crawling:
            await interaction.response.send_message("⏳ 크롤링이 이미 진행 중입니다. 잠시 후 다시 시도해주세요.")
            return

        await interaction.response.send_message("🔄 크롤링을 시작합니다... (30개 사이트, 약 2-5분 소요)")

        try:
            articles = await bot.do_crawl()
            await interaction.followup.send(
                f"✅ 크롤링 완료! **{len(articles)}개** 기사를 수집했습니다.\n"
                f"`/report` 명령어로 리포트를 생성할 수 있습니다."
            )
        except Exception as e:
            await interaction.followup.send(f"❌ 크롤링 실패: {e}")

    @bot.tree.command(name="report", description="수집된 기사로 주간 리포트를 생성합니다")
    async def cmd_report(interaction: discord.Interaction):
        if not bot.cached_articles:
            await interaction.response.send_message(
                "📭 수집된 기사가 없습니다. `/crawl`을 먼저 실행해주세요."
            )
            return

        await interaction.response.send_message("📊 리포트 생성 중...")

        try:
            report = bot.generate_report(bot.cached_articles)
            chunks = _split_message(report)

            for chunk in chunks:
                await interaction.followup.send(chunk)
        except Exception as e:
            await interaction.followup.send(f"❌ 리포트 생성 실패: {e}")

    @bot.tree.command(name="status", description="봇 상태와 마지막 크롤링 정보를 확인합니다")
    async def cmd_status(interaction: discord.Interaction):
        status_lines = [
            "📡 **Market Trend Crawler 상태**",
            f"• 등록된 사이트: **{len(bot.crawl_tasks)}개** (한국 {len(KOREAN_SITES_CONFIG)}개 + 해외 {len(INTERNATIONAL_SITES)}개)",
            f"• 크롤링 중: {'예' if bot._crawling else '아니오'}",
        ]

        if bot.last_crawl_time:
            elapsed = datetime.now() - bot.last_crawl_time
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            status_lines.append(f"• 마지막 크롤링: **{hours}시간 {minutes}분 전** ({bot.last_article_count}개 기사)")
        else:
            status_lines.append("• 마지막 크롤링: 아직 없음")

        status_lines.append(f"• 캐시된 기사: **{len(bot.cached_articles)}개**")
        status_lines.append(f"• 자동 크롤링: 매일 10:00, 17:00 (KST)")

        await interaction.response.send_message("\n".join(status_lines))

    @bot.tree.command(name="sites", description="크롤링 대상 사이트 목록을 확인합니다")
    async def cmd_sites(interaction: discord.Interaction):
        lines = ["📋 **크롤링 대상 사이트**\n"]

        lines.append("**🇰🇷 한국 사이트**")
        for config in KOREAN_SITES_CONFIG:
            status = "✅" if config.enabled else "❌"
            lines.append(f"  {status} {config.name} — {config.url}")

        lines.append("\n**🌍 해외 사이트**")
        for config in INTERNATIONAL_SITES:
            status = "✅" if config.enabled else "❌"
            lines.append(f"  {status} {config.name} — {config.url}")

        text = "\n".join(lines)
        for chunk in _split_message(text):
            if chunk == _split_message(text)[0]:
                await interaction.response.send_message(chunk)
            else:
                await interaction.followup.send(chunk)

    return bot
