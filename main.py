"""Entry point for Market Trend Crawler."""

import asyncio

from dotenv import load_dotenv

from market_trend_crawler.weekly_scheduler import main

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
