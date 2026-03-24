"""Configuration for international tech news and blog site crawlers.

This module provides configuration for 15 popular international tech news and blog sites.
Each site configuration includes metadata such as name, URL, language, and category mappings.
"""

from dataclasses import dataclass, field
from typing import Optional

from ..classification import classify_article
from ..models import SourceLanguage, Category


@dataclass
class InternationalSiteConfig:
    """Configuration for an international tech news/blog site.

    Attributes:
        name: Site name
        url: Base URL
        crawler_class: Crawler class name (string for lazy loading)
        language: Content language
        enabled: Whether the site is enabled for crawling
        category_mapping: Dictionary mapping URL patterns to categories
        notes: Optional description or notes about the site
    """
    name: str
    url: str
    crawler_class: str
    language: SourceLanguage
    enabled: bool = True
    category_mapping: dict[str, Category] = field(default_factory=dict)
    notes: Optional[str] = None


# Configuration for all 15 international tech news/blog sites
INTERNATIONAL_SITES = [
    InternationalSiteConfig(
        name="TechCrunch",
        url="https://techcrunch.com",
        crawler_class="TechCrunchCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Leading technology media property, covering startups, new Internet products, and tech news"
    ),
    InternationalSiteConfig(
        name="The Verge",
        url="https://www.theverge.com",
        crawler_class="TheVergeCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Covers intersection of technology, science, art, and culture"
    ),
    InternationalSiteConfig(
        name="Engadget",
        url="https://www.engadget.com",
        crawler_class="EngadgetCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Multilingual technology blog network covering gadgets and consumer electronics"
    ),
    InternationalSiteConfig(
        name="Wired",
        url="https://www.wired.com",
        crawler_class="WiredCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Monthly magazine focusing on emerging technologies' impact on culture, economy, and politics"
    ),
    InternationalSiteConfig(
        name="Ars Technica",
        url="https://arstechnica.com",
        crawler_class="ArsTechnicaCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Covers news and opinions in technology, science, politics, and society"
    ),
    InternationalSiteConfig(
        name="VentureBeat",
        url="https://venturebeat.com",
        crawler_class="VentureBeatCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Transforms enterprise technology coverage"
    ),
    InternationalSiteConfig(
        name="Hacker News",
        url="https://news.ycombinator.com",
        crawler_class="HackerNewsCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Social news website focusing on computer science and entrepreneurship (Y Combinator)"
    ),
    InternationalSiteConfig(
        name="Medium Tech",
        url="https://medium.com/tag/technology",
        crawler_class="MediumTechCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=False,
        notes="Publishing platform with a strong tech community"
    ),
    InternationalSiteConfig(
        name="ReadWrite",
        url="https://readwrite.com",
        crawler_class="ReadWriteCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Leading publication for the developer community covering technology and innovation"
    ),
    InternationalSiteConfig(
        name="Gigaom",
        url="https://gigaom.com",
        crawler_class="GigaomCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Research and emerging technology news for business and IT leaders"
    ),
    InternationalSiteConfig(
        name="Gizmodo",
        url="https://gizmodo.com",
        crawler_class="GizmodoCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Design, technology, science and science fiction website"
    ),
    InternationalSiteConfig(
        name="PCMag",
        url="https://www.pcmag.com",
        crawler_class="PCMagCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=False,
        notes="Complete guide to PC computers, peripherals and upgrades"
    ),
    InternationalSiteConfig(
        name="TechRadar",
        url="https://www.techradar.com",
        crawler_class="TechRadarCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=False,
        notes="Source for tech buying advice, news and reviews"
    ),
    InternationalSiteConfig(
        name="Mashable",
        url="https://mashable.com",
        crawler_class="MashableCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Global digital media and entertainment company"
    ),
    InternationalSiteConfig(
        name="Nextgov",
        url="https://www.nextgov.com",
        crawler_class="NextgovCrawler",
        language=SourceLanguage.ENGLISH,
        enabled=True,
        notes="Leading source of news and information for technology leaders in the public sector"
    ),
]


def get_enabled_sites() -> list[InternationalSiteConfig]:
    """Get all enabled international site configurations.

    Returns:
        List of enabled site configurations
    """
    return [site for site in INTERNATIONAL_SITES if site.enabled]


def get_site_by_name(name: str) -> Optional[InternationalSiteConfig]:
    """Find a specific site configuration by name.

    Args:
        name: Site name to search for

    Returns:
        Site configuration if found, None otherwise
    """
    for site in INTERNATIONAL_SITES:
        if site.name.lower() == name.lower():
            return site
    return None


def get_sites_by_category(category: Category) -> list[InternationalSiteConfig]:
    """Find all sites with specific category mappings.

    Args:
        category: Category to filter by

    Returns:
        List of site configurations with the specified category
    """
    return [site for site in INTERNATIONAL_SITES if category in site.category_mapping.values()]


def get_all_sites() -> list[InternationalSiteConfig]:
    """Get all international site configurations (both enabled and disabled).

    Returns:
        List of all site configurations
    """
    return INTERNATIONAL_SITES.copy()


def categorize_by_keywords(url: str, title: str) -> Category:
    """Categorize an article based on URL and title keywords.

    This is a wrapper around the centralized classify_article function.
    It maintains backward compatibility with existing code.

    Args:
        url: Article URL
        title: Article title

    Returns:
        Detected category
    """
    return classify_article(url, title)


# Statistics helper functions
def get_statistics() -> dict[str, any]:
    """Get statistics about international site configurations.

    Returns:
        Dictionary containing site statistics
    """
    return {
        "total_sites": len(INTERNATIONAL_SITES),
        "enabled_sites": len(get_enabled_sites()),
        "disabled_sites": len(INTERNATIONAL_SITES) - len(get_enabled_sites()),
        "english_sites": len([s for s in INTERNATIONAL_SITES if s.language == SourceLanguage.ENGLISH]),
        "korean_sites": len([s for s in INTERNATIONAL_SITES if s.language == SourceLanguage.KOREAN]),
        "sites_by_category": {
            category.name: len(get_sites_by_category(category))
            for category in Category
        }
    }


__all__ = [
    "InternationalSiteConfig",
    "INTERNATIONAL_SITES",
    "get_enabled_sites",
    "get_site_by_name",
    "get_sites_by_category",
    "get_all_sites",
    "categorize_by_keywords",
    "get_statistics",
]
