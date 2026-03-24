"""Nextgov crawler.

Nextgov is the leading source of news and information for technology leaders in the public sector.
"""

from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ..models import Article, Category, SourceLanguage
from ..classification import classify_article


class NextgovCrawler(BaseCrawler):
    """Crawler for Nextgov - https://www.nextgov.com"""

    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        """Extract articles from Nextgov.

        Args:
            html: HTML content
            source: Source name
            language: Content language

        Returns:
            List of extracted articles
        """
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Nextgov uses div.river-item-inner containers or h2 a links
        seen_urls = set()

        # Try river items first
        river_items = soup.select("div.river-item-inner")
        if river_items:
            for item in river_items:
                try:
                    link_elem = item.select_one("h2 a")
                    if not link_elem:
                        continue

                    url = link_elem.get("href", "")
                    if not url:
                        continue
                    if not url.startswith("http"):
                        url = f"https://www.nextgov.com{url}"

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = link_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    content = title
                    published_at = datetime.now()

                    time_elem = item.find("time")
                    if time_elem:
                        datetime_str = time_elem.get("datetime", "")
                        if datetime_str:
                            try:
                                published_at = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass

                    category = self._determine_category(url, title)

                    article = Article(
                        title=title,
                        url=url,
                        content=content[:500],
                        source=source,
                        published_at=published_at,
                        category=category,
                        language=SourceLanguage.ENGLISH,
                    )
                    articles.append(article)

                except Exception as e:
                    continue
        else:
            # Fallback: find all h2 a links
            for link_elem in soup.select("h2 a[href]"):
                try:
                    url = link_elem.get("href", "")
                    if not url:
                        continue
                    if not url.startswith("http"):
                        url = f"https://www.nextgov.com{url}"

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = link_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    content = title
                    published_at = datetime.now()

                    category = self._determine_category(url, title)

                    article = Article(
                        title=title,
                        url=url,
                        content=content[:500],
                        source=source,
                        published_at=published_at,
                        category=category,
                        language=SourceLanguage.ENGLISH,
                    )
                    articles.append(article)

                except Exception as e:
                    continue

        return articles

    def _determine_category(self, url: str, title: str) -> Category:
        """Determine category from URL and title using centralized classification.

        Args:
            url: Article URL
            title: Article title

        Returns:
            Category enum value
        """
        return classify_article(url, title)
