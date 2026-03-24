"""Configuration for Korean news and blog sites."""

from dataclasses import dataclass
from typing import Optional

from .models import Category, SourceLanguage


@dataclass
class KoreanSiteConfig:
    """Configuration for a Korean news/blog site."""

    name: str
    url: str
    crawler_class: str
    language: SourceLanguage = SourceLanguage.KOREAN
    enabled: bool = True
    category_mapping: Optional[dict[str, Category]] = None
    notes: Optional[str] = None


# Configuration for all 15 Korean tech news/blog sites
KOREAN_SITES_CONFIG = [
    KoreanSiteConfig(
        name="Bloter",
        url="https://www.bloter.net",
        crawler_class="BloterCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/ai": Category.AI_ML,
            "/startup": Category.STARTUP_BUSINESS,
            "/blockchain": Category.BLOCKCHAIN_WEB3,
        },
        notes="Korean tech news covering AI, startups, and technology trends",
    ),
    KoreanSiteConfig(
        name="TechM",
        url="https://techm.kr",
        crawler_class="TechMCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/category/ai": Category.AI_ML,
            "/category/startup": Category.STARTUP_BUSINESS,
        },
        notes="Korean tech media focusing on startups and technology",
    ),
    KoreanSiteConfig(
        name="ZDNet Korea",
        url="https://zdnet.co.kr",
        crawler_class="ZDNetKoreaCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/cloud": Category.DEVOPS_CLOUD,
            "/security": Category.DEVOPS_CLOUD,
        },
        notes="Korean IT news site covering enterprise technology",
    ),
    KoreanSiteConfig(
        name="ITWorld Korea",
        url="https://www.itworld.co.kr",
        crawler_class="ITWorldKoreaCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/ai": Category.AI_ML,
            "/cloud": Category.DEVOPS_CLOUD,
        },
        notes="Korean IT news for enterprise and technology professionals",
    ),
    KoreanSiteConfig(
        name="CIO Korea",
        url="https://www.ciokorea.com",
        crawler_class="CIOKoreaCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/ai": Category.AI_ML,
            "/cloud": Category.DEVOPS_CLOUD,
        },
        notes="Korean IT media for CIOs and IT professionals",
    ),
    KoreanSiteConfig(
        name="B2News",
        url="https://www.b2news.co.kr",
        crawler_class="B2NewsCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        notes="Korean B2B tech news site",
    ),
    KoreanSiteConfig(
        name="Digital Daily",
        url="https://www.ddaily.co.kr",
        crawler_class="DigitalDailyCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        notes="Korean tech and economy news site",
    ),
    KoreanSiteConfig(
        name="Herald Tech",
        url="https://biz.heraldcorp.com",
        crawler_class="HeraldTechCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        notes="Tech section of Herald Economy",
    ),
    KoreanSiteConfig(
        name="MK Tech",
        url="https://www.mk.co.kr",
        crawler_class="MKTechCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/it": Category.DEVOPS_CLOUD,
            "/semiconductor": Category.TECH_PRODUCTS,
        },
        notes="Tech section of MK Business",
    ),
    KoreanSiteConfig(
        name="Hankyung Tech",
        url="https://www.hankyung.com",
        crawler_class="HankyungTechCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/startup": Category.STARTUP_BUSINESS,
            "/semiconductor": Category.TECH_PRODUCTS,
        },
        notes="Tech section of Korea Economic Daily",
    ),
    KoreanSiteConfig(
        name="The Elec",
        url="https://www.thelec.co.kr",
        crawler_class="TheElecCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        category_mapping={
            "/semiconductor": Category.TECH_PRODUCTS,
        },
        notes="Korean tech news covering electronics and semiconductors",
    ),
    KoreanSiteConfig(
        name="Naver Tech",
        url="https://d2.naver.com",
        crawler_class="NaverTechCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        notes="Naver's developer and tech blog",
    ),
    KoreanSiteConfig(
        name="Danawa Tech",
        url="https://blog.danawa.com",
        crawler_class="DanawaTechCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        notes="Tech blog from Danawa, a Korean price comparison site",
    ),
    KoreanSiteConfig(
        name="Brunch Tech",
        url="https://brunch.co.kr",
        crawler_class="BrunchTechCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        notes="Tech-focused content from Brunch, a Korean blogging platform",
    ),
    KoreanSiteConfig(
        name="OKKY",
        url="https://okky.kr",
        crawler_class="OKKYCrawler",
        language=SourceLanguage.KOREAN,
        enabled=True,
        notes="Korean developer community and tech blog platform",
    ),
]


def get_enabled_sites() -> list[KoreanSiteConfig]:
    """Get all enabled Korean site configurations.

    Returns:
        List of enabled site configurations
    """
    return [site for site in KOREAN_SITES_CONFIG if site.enabled]


def get_site_by_name(name: str) -> Optional[KoreanSiteConfig]:
    """Get site configuration by name.

    Args:
        name: Site name

    Returns:
        Site configuration or None if not found
    """
    for site in KOREAN_SITES_CONFIG:
        if site.name == name:
            return site
    return None


def get_sites_by_category(category: Category) -> list[KoreanSiteConfig]:
    """Get sites that have content in a specific category.

    Args:
        category: Category to filter by

    Returns:
        List of site configurations with matching category
    """
    matching_sites = []
    for site in KOREAN_SITES_CONFIG:
        if site.category_mapping and category in site.category_mapping.values():
            matching_sites.append(site)
    return matching_sites
