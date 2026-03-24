"""Entry point for running as a module: python -m market_trend_crawler"""

import asyncio

from .weekly_scheduler import main

if __name__ == "__main__":
    asyncio.run(main())
