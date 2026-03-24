"""Report categorization and aggregation system for weekly Discord reports.

This module provides categorization and aggregation logic specifically designed
for generating weekly Discord reports from crawled tech news articles.

It transforms individual articles into organized report sections based on
various categorization dimensions:
- Report sections (Top Stories, Trending Topics, etc.)
- Category breakdown (AI_ML, BLOCKCHAIN_WEB3, etc.)
- Language distribution (Korean vs International)
- Source contribution (which sites provided most content)
"""

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List

from .models import Article, Category, SourceLanguage

logger = logging.getLogger(__name__)


# Report section types for Discord weekly reports
class ReportSection(str, Enum):
    """Report sections for organizing articles in Discord weekly reports."""

    TOP_STORIES = "TOP_STORIES"
    TRENDING_TOPICS = "TRENDING_TOPICS"
    CATEGORY_BREAKDOWN = "CATEGORY_BREAKDOWN"
    MOST_DISCUSSED = "MOST_DISCUSSED"
    EDITORS_PICKS = "EDITORS_PICKS"
    NEW_THIS_WEEK = "NEW_THIS_WEEK"
    WEEKLY_DIGEST = "WEEKLY_DIGEST"


# Report priorities for article ranking
class ReportPriority(str, Enum):
    """Priority levels for articles in reports."""

    CRITICAL = "CRITICAL"  # Breaking news, major announcements
    HIGH = "HIGH"  # Important developments
    MEDIUM = "MEDIUM"  # Regular news
    LOW = "LOW"  # Minor updates, filler content


@dataclass
class CategoryStats:
    """Statistics for a specific category in a report."""

    category: Category
    count: int
    percentage: float
    top_sources: list[tuple[str, int]]
    top_keywords: list[tuple[str, int]]
    avg_article_length: float


@dataclass
class ReportAggregation:
    """Aggregated data for weekly Discord report."""

    period_start: datetime
    period_end: datetime
    total_articles: int
    by_category: dict[Category, list[Article]]
    by_language: dict[SourceLanguage, list[Article]]
    by_source: dict[str, list[Article]]
    category_stats: dict[Category, CategoryStats]
    trending_keywords: list[tuple[str, int]]
    top_sources: list[tuple[str, int]]
    sections: dict[str, list[Article]]


@dataclass
class ArticleScore:
    """Score for ranking articles in reports."""

    article: Article
    priority: ReportPriority
    score: float
    reasoning: list[str]


def categorize_for_report(
    articles: list[Article],
    period_start: datetime,
    period_end: datetime,
) -> ReportAggregation:
    """Categorize and aggregate articles for weekly report generation.

    This function organizes articles into various categories and dimensions
    suitable for generating a comprehensive Discord weekly report.

    Args:
        articles: List of articles to categorize
        period_start: Start of the report period
        period_end: End of the report period

    Returns:
        ReportAggregation object with categorized and aggregated data
    """
    # Filter articles within the period
    period_articles = [
        a for a in articles
        if period_start <= a.published_at <= period_end
    ]

    logger.info(
        f"Categorizing {len(period_articles)} articles "
        f"for report period {period_start.date()} to {period_end.date()}"
    )

    # Organize articles by various dimensions
    by_category = _group_by_category(period_articles)
    by_language = _group_by_language(period_articles)
    by_source = _group_by_source(period_articles)

    # Calculate category statistics
    category_stats = _calculate_category_stats(
        by_category,
        by_source,
        len(period_articles)
    )

    # Extract trending keywords
    trending_keywords = _extract_trending_keywords(period_articles)

    # Get top sources
    top_sources = _get_top_sources(by_source)

    # Create report sections
    sections = _create_report_sections(
        period_articles,
        by_category,
        by_source,
        category_stats,
        trending_keywords
    )

    aggregation = ReportAggregation(
        period_start=period_start,
        period_end=period_end,
        total_articles=len(period_articles),
        by_category=by_category,
        by_language=by_language,
        by_source=by_source,
        category_stats=category_stats,
        trending_keywords=trending_keywords,
        top_sources=top_sources,
        sections=sections
    )

    logger.info(f"Report aggregation complete: {len(period_articles)} articles "
                f"across {len(by_category)} categories")

    return aggregation


def _group_by_category(articles: list[Article]) -> dict[Category, list[Article]]:
    """Group articles by their category.

    Args:
        articles: List of articles

    Returns:
        Dictionary mapping categories to article lists
    """
    grouped = defaultdict(list)
    for article in articles:
        grouped[article.category].append(article)
    return dict(grouped)


def _group_by_language(articles: list[Article]) -> dict[SourceLanguage, list[Article]]:
    """Group articles by their language.

    Args:
        articles: List of articles

    Returns:
        Dictionary mapping languages to article lists
    """
    grouped = defaultdict(list)
    for article in articles:
        grouped[article.language].append(article)
    return dict(grouped)


def _group_by_source(articles: list[Article]) -> dict[str, list[Article]]:
    """Group articles by their source.

    Args:
        articles: List of articles

    Returns:
        Dictionary mapping source names to article lists
    """
    grouped = defaultdict(list)
    for article in articles:
        grouped[article.source].append(article)
    return dict(grouped)


def _calculate_category_stats(
    by_category: dict[Category, list[Article]],
    by_source: dict[str, list[Article]],
    total_articles: int
) -> dict[Category, CategoryStats]:
    """Calculate statistics for each category.

    Args:
        by_category: Articles grouped by category
        by_source: Articles grouped by source
        total_articles: Total number of articles

    Returns:
        Dictionary mapping categories to their statistics
    """
    stats = {}

    for category, articles in by_category.items():
        count = len(articles)
        percentage = (count / total_articles * 100) if total_articles > 0 else 0

        # Get top sources for this category
        source_counter = Counter(a.source for a in articles)
        top_sources = source_counter.most_common(5)

        # Get top keywords from titles
        all_keywords = []
        for article in articles:
            # Simple keyword extraction from title
            words = [w.lower() for w in article.title.split()
                     if len(w) > 3]  # Filter short words
            all_keywords.extend(words)

        keyword_counter = Counter(all_keywords)
        top_keywords = keyword_counter.most_common(10)

        # Calculate average article length
        avg_length = sum(len(a.content) for a in articles) / count if count > 0 else 0

        stats[category] = CategoryStats(
            category=category,
            count=count,
            percentage=round(percentage, 1),
            top_sources=top_sources,
            top_keywords=top_keywords,
            avg_article_length=round(avg_length, 0)
        )

    return stats


def _extract_trending_keywords(articles: list[Article]) -> list[tuple[str, int]]:
    """Extract trending keywords from all articles.

    Args:
        articles: List of articles

    Returns:
        List of (keyword, count) tuples sorted by frequency
    """
    all_keywords = []

    for article in articles:
        # Extract keywords from title
        title_words = [
            w.lower().strip('.,!?;:"\'')
            for w in article.title.split()
            if len(w) > 3 and w.lower() not in {'this', 'that', 'with', 'from'}
        ]
        all_keywords.extend(title_words)

        # Extract keywords from tags if available
        if article.tags:
            all_keywords.extend([tag.lower() for tag in article.tags if len(tag) > 2])

    keyword_counter = Counter(all_keywords)
    return keyword_counter.most_common(20)


def _get_top_sources(
    by_source: dict[str, list[Article]]
) -> list[tuple[str, int]]:
    """Get top sources by article count.

    Args:
        by_source: Articles grouped by source

    Returns:
        List of (source, count) tuples sorted by article count
    """
    source_counts = {source: len(articles) for source, articles in by_source.items()}
    return sorted(source_counts.items(), key=lambda x: x[1], reverse=True)


def _create_report_sections(
    articles: list[Article],
    by_category: dict[Category, list[Article]],
    by_source: dict[str, list[Article]],
    category_stats: dict[Category, CategoryStats],
    trending_keywords: list[tuple[str, int]]
) -> dict[str, list[Article]]:
    """Create report sections with selected articles.

    Args:
        articles: All articles
        by_category: Articles grouped by category
        by_source: Articles grouped by source
        category_stats: Category statistics
        trending_keywords: Trending keywords

    Returns:
        Dictionary mapping section names to article lists
    """
    sections = {}

    # TOP_STORIES: Top 5-10 articles overall
    sections[ReportSection.TOP_STORIES] = _get_top_stories(articles, limit=10)

    # TRENDING_TOPICS: Articles with trending keywords
    sections[ReportSection.TRENDING_TOPICS] = _get_trending_topic_articles(
        articles, trending_keywords, limit=15
    )

    # MOST_DISCUSSED: Most articles per source (most active sources)
    sections[ReportSection.MOST_DISCUSSED] = _get_most_discussed_articles(
        by_source, limit=10
    )

    # EDITORS_PICKS: Longest articles (in-depth coverage)
    sections[ReportSection.EDITORS_PICKS] = _get_editors_picks(articles, limit=8)

    # NEW_THIS_WEEK: Most recent articles
    sections[ReportSection.NEW_THIS_WEEK] = _get_newest_articles(articles, limit=12)

    # WEEKLY_DIGEST: One or two articles from each major category
    sections[ReportSection.WEEKLY_DIGEST] = _get_weekly_digest(
        by_category, category_stats, limit_per_category=2
    )

    return sections


def _get_top_stories(articles: list[Article], limit: int = 10) -> list[Article]:
    """Get top stories based on multiple factors.

    Ranking considers:
    - Article length (longer = more in-depth)
    - Category importance (AI_ML, STARTUP_BUSINESS get higher weight)
    - Source quality (well-known sources preferred)

    Args:
        articles: List of articles
        limit: Maximum number of articles to return

    Returns:
        List of top articles
    """
    scored_articles = []

    # Category weights
    category_weights = {
        Category.AI_ML: 1.5,
        Category.STARTUP_BUSINESS: 1.3,
        Category.BLOCKCHAIN_WEB3: 1.2,
        Category.DEVOPS_CLOUD: 1.1,
        Category.TECH_PRODUCTS: 1.0,
        Category.OTHER: 0.8,
    }

    for article in articles:
        # Score based on length, category, and tags
        length_score = min(len(article.content) / 1000, 5)  # Max 5 points for length
        category_score = category_weights.get(article.category, 1.0)
        tags_score = min(len(article.tags) / 5, 2)  # Max 2 points for tags

        total_score = length_score * category_score + tags_score

        scored_articles.append((article, total_score))

    # Sort by score and return top
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    return [article for article, _ in scored_articles[:limit]]


def _get_trending_topic_articles(
    articles: list[Article],
    trending_keywords: list[tuple[str, int]],
    limit: int = 15
) -> list[Article]:
    """Get articles related to trending topics.

    Args:
        articles: List of articles
        trending_keywords: List of trending keywords with counts
        limit: Maximum number of articles to return

    Returns:
        List of articles related to trending topics
    """
    selected = []
    seen_urls = set()

    # Get top trending keywords
    top_keywords = [kw for kw, count in trending_keywords[:15]]

    for article in articles:
        if len(selected) >= limit:
            break

        if article.url in seen_urls:
            continue

        # Check if article contains trending keywords
        title_lower = article.title.lower()

        for keyword in top_keywords:
            if keyword in title_lower:
                selected.append(article)
                seen_urls.add(article.url)
                break

    return selected


def _get_most_discussed_articles(
    by_source: dict[str, list[Article]],
    limit: int = 10
) -> list[Article]:
    """Get articles from the most active sources.

    Args:
        by_source: Articles grouped by source
        limit: Maximum number of articles to return

    Returns:
        List of articles from active sources
    """
    # Sort sources by article count
    sorted_sources = sorted(
        by_source.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    # Take articles from top sources
    articles = []
    articles_per_source = 2  # Take 2 from each top source

    for source, source_articles in sorted_sources:
        if len(articles) >= limit:
            break

        articles.extend(source_articles[:articles_per_source])

    return articles[:limit]


def _get_editors_picks(articles: list[Article], limit: int = 8) -> list[Article]:
    """Get in-depth articles (longer, more detailed content).

    Args:
        articles: List of articles
        limit: Maximum number of articles to return

    Returns:
        List of in-depth articles
    """
    # Sort by content length
    sorted_articles = sorted(
        articles,
        key=lambda a: len(a.content),
        reverse=True
    )

    return sorted_articles[:limit]


def _get_newest_articles(articles: list[Article], limit: int = 12) -> list[Article]:
    """Get the most recently published articles.

    Args:
        articles: List of articles
        limit: Maximum number of articles to return

    Returns:
        List of newest articles
    """
    # Sort by published date
    sorted_articles = sorted(
        articles,
        key=lambda a: a.published_at,
        reverse=True
    )

    return sorted_articles[:limit]


def _get_weekly_digest(
    by_category: dict[Category, list[Article]],
    category_stats: dict[Category, CategoryStats],
    limit_per_category: int = 2
) -> list[Article]:
    """Get a digest with articles from each major category.

    Args:
        by_category: Articles grouped by category
        category_stats: Category statistics
        limit_per_category: Maximum articles per category

    Returns:
        List of articles representing weekly digest
    """
    digest = []

    # Sort categories by article count (most active categories first)
    sorted_categories = sorted(
        by_category.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for category, articles in sorted_categories:
        # Take top articles from this category
        top_articles = sorted(
            articles,
            key=lambda a: len(a.content),
            reverse=True
        )

        digest.extend(top_articles[:limit_per_category])

    return digest


def score_article_for_report(article: Article) -> ArticleScore:
    """Score an article for prioritization in reports.

    Scoring considers multiple factors:
    - Content length (longer = more in-depth)
    - Category importance
    - Recency
    - Source quality
    - Tags and metadata

    Args:
        article: Article to score

    Returns:
        ArticleScore object with priority and score
    """
    reasoning = []

    # Category weights
    category_weights = {
        Category.AI_ML: 1.5,
        Category.STARTUP_BUSINESS: 1.3,
        Category.BLOCKCHAIN_WEB3: 1.2,
        Category.DEVOPS_CLOUD: 1.1,
        Category.TECH_PRODUCTS: 1.0,
        Category.OTHER: 0.8,
    }

    # Score components
    length_score = min(len(article.content) / 1000, 5.0)
    category_score = category_weights.get(article.category, 1.0)
    tags_score = min(len(article.tags) / 5, 2.0)

    # Recency score (articles within 3 days get bonus)
    days_old = (datetime.now() - article.published_at).days
    if days_old <= 1:
        recency_score = 1.5
        reasoning.append("Very recent (< 24 hours)")
    elif days_old <= 3:
        recency_score = 1.2
        reasoning.append("Recent (< 3 days)")
    elif days_old <= 7:
        recency_score = 1.0
        reasoning.append("Recent (< 1 week)")
    else:
        recency_score = 0.8
        reasoning.append("Older (> 1 week)")

    # Calculate total score
    total_score = (
        length_score * category_score +
        tags_score * category_score +
        recency_score
    )

    # Determine priority
    if total_score >= 7.0:
        priority = ReportPriority.CRITICAL
        reasoning.append("Critical importance")
    elif total_score >= 5.0:
        priority = ReportPriority.HIGH
        reasoning.append("High importance")
    elif total_score >= 3.0:
        priority = ReportPriority.MEDIUM
        reasoning.append("Medium importance")
    else:
        priority = ReportPriority.LOW
        reasoning.append("Standard importance")

    return ArticleScore(
        article=article,
        priority=priority,
        score=round(total_score, 2),
        reasoning=reasoning
    )


def get_report_summary(aggregation: ReportAggregation) -> dict:
    """Generate a summary of the report aggregation.

    Args:
        aggregation: ReportAggregation object

    Returns:
        Dictionary with summary statistics
    """
    korean_count = len(aggregation.by_language.get(SourceLanguage.KOREAN, []))
    english_count = len(aggregation.by_language.get(SourceLanguage.ENGLISH, []))

    return {
        "period": {
            "start": aggregation.period_start.date().isoformat(),
            "end": aggregation.period_end.date().isoformat(),
            "days": (aggregation.period_end - aggregation.period_start).days
        },
        "total_articles": aggregation.total_articles,
        "language_breakdown": {
            "korean": korean_count,
            "english": english_count,
            "korean_percentage": round(korean_count / aggregation.total_articles * 100, 1)
            if aggregation.total_articles > 0 else 0
        },
        "category_breakdown": {
            cat.value: stats.count
            for cat, stats in aggregation.category_stats.items()
        },
        "top_sources": aggregation.top_sources[:5],
        "trending_keywords": aggregation.trending_keywords[:10],
        "sections": {
            section: len(articles)
            for section, articles in aggregation.sections.items()
        }
    }


# Export public API
__all__ = [
    "ReportSection",
    "ReportPriority",
    "CategoryStats",
    "ReportAggregation",
    "ArticleScore",
    "categorize_for_report",
    "score_article_for_report",
    "get_report_summary",
]
