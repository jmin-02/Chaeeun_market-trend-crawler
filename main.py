"""Entry point for Market Trend Crawler Discord Bot."""

import logging
import os

from dotenv import load_dotenv

from market_trend_crawler.bot import create_bot


def main():
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("DISCORD_BOT_TOKEN not set in .env")

    bot = create_bot()
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
