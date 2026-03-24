"""Scheduler for automated daily crawling."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Awaitable, Callable, Optional

from pydantic import BaseModel

from .base import BaseCrawler
from .models import Article

logger = logging.getLogger(__name__)


@dataclass
class ScheduleConfig:
    """Configuration for daily scheduler."""

    # Daily run times (default: 10 AM and 5 PM)
    run_times: list[time] = None

    def __post_init__(self) -> None:
        if self.run_times is None:
            self.run_times = [time(10, 0), time(17, 0)]


class ScheduleTask(BaseModel):
    """Task to be scheduled."""

    name: str
    url: str
    source: str
    language: str = "en"
    enabled: bool = True


class DailyScheduler:
    """Scheduler for running crawler tasks at specific times daily.

    Supports:
    - Multiple daily run times
    - Task registration and management
    - Async task execution
    - Graceful shutdown
    """

    def __init__(
        self,
        config: Optional[ScheduleConfig] = None,
        crawler: Optional[BaseCrawler] = None,
    ) -> None:
        """Initialize scheduler.

        Args:
            config: Schedule configuration
            crawler: Optional crawler instance (creates default if None)
        """
        self.config = config or ScheduleConfig()
        self.crawler = crawler or BaseCrawler()
        self.tasks: list[ScheduleTask] = []
        self._running = False
        self._stop_event = asyncio.Event()

    def register_task(self, task: ScheduleTask) -> None:
        """Register a crawling task.

        Args:
            task: Task to register
        """
        self.tasks.append(task)
        logger.info(f"Registered task: {task.name} -> {task.url}")

    def register_tasks(self, tasks: list[ScheduleTask]) -> None:
        """Register multiple tasks.

        Args:
            tasks: List of tasks to register
        """
        for task in tasks:
            self.register_task(task)

    async def _execute_task(self, task: ScheduleTask) -> list[Article]:
        """Execute a single task.

        Args:
            task: Task to execute

        Returns:
            List of crawled articles
        """
        if not task.enabled:
            logger.info(f"Skipping disabled task: {task.name}")
            return []

        logger.info(f"Executing task: {task.name}")
        try:
            articles = await self.crawler.crawl(task.url, task.source, task.language)
            logger.info(f"Task {task.name} completed: {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"Task {task.name} failed: {e}", exc_info=True)
            return []

    async def _run_cycle(self) -> dict[str, list[Article]]:
        """Run all tasks for current cycle.

        Returns:
            Dictionary mapping task names to articles
        """
        results: dict[str, list[Article]] = {}

        logger.info(f"Starting crawl cycle with {len(self.tasks)} tasks")

        # Run tasks concurrently with some concurrency control
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent tasks

        async def run_with_semaphore(task: ScheduleTask) -> tuple[str, list[Article]]:
            async with semaphore:
                return (task.name, await self._execute_task(task))

        # Execute all tasks
        tasks_coroutines = [run_with_semaphore(task) for task in self.tasks]
        results_list = await asyncio.gather(*tasks_coroutines, return_exceptions=True)

        # Process results
        for result in results_list:
            if isinstance(result, Exception):
                logger.error(f"Task execution failed: {result}", exc_info=result)
            else:
                name, articles = result
                results[name] = articles

        # Log statistics
        total_articles = sum(len(articles) for articles in results.values())
        logger.info(
            f"Crawl cycle completed: {len(results)} tasks, {total_articles} total articles"
        )

        return results

    async def _wait_until_next_run(self) -> None:
        """Wait until next scheduled run time."""
        now = datetime.now()
        current_time = now.time()

        # Find next run time
        next_run_time = None
        for run_time in sorted(self.config.run_times):
            if current_time < run_time:
                next_run_time = run_time
                break

        # If no run time today, schedule for tomorrow
        if next_run_time is None:
            next_run_time = self.config.run_times[0]
            tomorrow = now + timedelta(days=1)
            next_run = datetime.combine(tomorrow.date(), next_run_time)
        else:
            next_run = datetime.combine(now.date(), next_run_time)

        wait_seconds = (next_run - now).total_seconds()

        logger.info(
            f"Next scheduled run at {next_run.strftime('%Y-%m-%d %H:%M:%S')} "
            f"(waiting {wait_seconds:.0f} seconds)"
        )

        await asyncio.sleep(wait_seconds)

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        logger.info(
            f"Starting scheduler with run times: "
            f"{[t.strftime('%H:%M') for t in self.config.run_times]}"
        )

        while not self._stop_event.is_set():
            try:
                # Run crawl cycle
                await self._run_cycle()

                # Wait for next run time
                await asyncio.wait_for(
                    self._wait_until_next_run(), timeout=3600.0
                )  # Check stop event every hour

            except asyncio.CancelledError:
                logger.info("Scheduler cancelled")
                break
            except asyncio.TimeoutError:
                # Timeout from wait_until_next_run - check stop event
                continue
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                # Wait a bit before retrying
                await asyncio.sleep(300)

        logger.info("Scheduler stopped")

    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._stop_event.clear()
        logger.info("Starting daily scheduler")

        # Start scheduler in background
        await self._scheduler_loop()

    async def stop(self) -> None:
        """Stop the scheduler gracefully."""
        if not self._running:
            return

        logger.info("Stopping scheduler")
        self._stop_event.set()
        self._running = False

        await self.crawler.close()

    async def run_once(self) -> dict[str, list[Article]]:
        """Run a single crawl cycle immediately.

        Returns:
            Dictionary mapping task names to articles
        """
        logger.info("Running immediate crawl cycle")
        return await self._run_cycle()

    def get_stats(self) -> dict[str, dict[str, int]]:
        """Get scheduler and crawler statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "scheduler": {
                "total_tasks": len(self.tasks),
                "enabled_tasks": sum(1 for t in self.tasks if t.enabled),
                "running": self._running,
                "run_times": [t.strftime("%H:%M") for t in self.config.run_times],
            },
            "crawler": self.crawler.get_stats(),
        }
