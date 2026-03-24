"""Discord message formatting templates for tech news categories.

This module provides Discord-compatible markdown formatting templates for
organizing and presenting crawled tech news articles in weekly Discord reports.

Features:
- Category-specific formatting templates (5 categories)
- Bilingual support (Korean + English)
- Discord markdown optimization
- Embeddable message formats
- Emoji-enhanced presentation
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Optional

from .models import Article, Category, SourceLanguage, InsightCategory
from .report_categorization import ReportAggregation
from .insight_extraction import (
    ExtractedInsight,
    ExtractedSkill,
    ExtractedCompany,
    ExtractedSalary,
    ExtractedJobTitle,
    ExtractedLocation,
)

logger = logging.getLogger(__name__)


# Discord markdown-safe characters need to be escaped
DISCORD_SPECIAL_CHARS = {
    '\\': '\\\\',
    '*': '\\*',
    '_': '\\_',
    '~': '\\~',
    '|': '\\|',
    '`': '\\`',
    '>': '\\>',
}


def escape_discord(text: str) -> str:
    """Escape Discord markdown special characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text safe for Discord markdown
    """
    if not text:
        return ""

    for char, escaped in DISCORD_SPECIAL_CHARS.items():
        text = text.replace(char, escaped)

    return text


class DiscordEmoji(str, Enum):
    """Discord emojis for categories and sections."""

    # Category emojis
    AI_ML = "🤖"
    BLOCKCHAIN_WEB3 = "⛓️"
    STARTUP_BUSINESS = "🚀"
    TECH_PRODUCTS = "📱"
    DEVOPS_CLOUD = "☁️"
    OTHER = "📰"

    # Section emojis
    TOP_STORIES = "🔥"
    TRENDING_TOPICS = "📈"
    CATEGORY_BREAKDOWN = "📊"
    MOST_DISCUSSED = "💬"
    EDITORS_PICKS = "⭐"
    NEW_THIS_WEEK = "✨"
    WEEKLY_DIGEST = "📋"

    # Status emojis
    KOREAN = "🇰🇷"
    ENGLISH = "🇺🇸"
    FRESH = "🆕"
    BREAKING = "🚨"
    HIGH_PRIORITY = "⬆️"
    LOW_PRIORITY = "⬇️"

    # Insight category emojis
    INSIGHT_HIRING_TRENDS = "📊"
    INSIGHT_IN_DEMAND_SKILLS = "💡"
    INSIGHT_COMPANY_NEWS = "🏢"
    INSIGHT_SALARY_BENEFITS = "💰"
    INSIGHT_CAREER_DEVELOPMENT = "📈"
    INSIGHT_JOB_OPENINGS = "🎯"
    INSIGHT_INDUSTRY_OUTLOOK = "🔮"
    INSIGHT_TECH_UPDATES = "⚙️"
    INSIGHT_WORKPLACE_CULTURE = "🏠"
    INSIGHT_EDUCATION_TRAINING = "📚"
    INSIGHT_OTHER = "📄"

    # Skill level emojis
    SKILL_JUNIOR = "🌱"
    SKILL_MID = "🌿"
    SKILL_SENIOR = "🌳"
    SKILL_LEAD = "🏆"
    SKILL_PRINCIPAL = "👑"
    SKILL_EXECUTIVE = "🎖️"

    # Company action emojis
    COMPANY_HIRING = "👥"
    COMPANY_FUNDING = "💵"
    COMPANY_ACQUISITION = "🤝"
    COMPANY_EXPANSION = "📍"
    COMPANY_IPO = "📈"
    COMPANY_LAYOFF = "📉"
    COMPANY_LAUNCH = "🚀"

    # Location type emojis
    LOCATION_CITY = "🏙️"
    LOCATION_COUNTRY = "🌍"
    LOCATION_REMOTE = "🏡"


class CategoryTemplate(str, Enum):
    """Template identifiers for category-specific formatting."""

    AI_ML = "AI_ML"
    BLOCKCHAIN_WEB3 = "BLOCKCHAIN_WEB3"
    STARTUP_BUSINESS = "STARTUP_BUSINESS"
    TECH_PRODUCTS = "TECH_PRODUCTS"
    DEVOPS_CLOUD = "DEVOPS_CLOUD"
    OTHER = "OTHER"


class SectionTemplate(str, Enum):
    """Template identifiers for section-specific formatting."""

    TOP_STORIES = "TOP_STORIES"
    TRENDING_TOPICS = "TRENDING_TOPICS"
    CATEGORY_BREAKDOWN = "CATEGORY_BREAKDOWN"
    MOST_DISCUSSED = "MOST_DISCUSSED"
    EDITORS_PICKS = "EDITORS_PICKS"
    NEW_THIS_WEEK = "NEW_THIS_WEEK"
    WEEKLY_DIGEST = "WEEKLY_DIGEST"


def get_category_emoji(category: Category) -> DiscordEmoji:
    """Get Discord emoji for a category.

    Args:
        category: Article category

    Returns:
        Discord emoji for the category
    """
    emoji_map = {
        Category.AI_ML: DiscordEmoji.AI_ML,
        Category.BLOCKCHAIN_WEB3: DiscordEmoji.BLOCKCHAIN_WEB3,
        Category.STARTUP_BUSINESS: DiscordEmoji.STARTUP_BUSINESS,
        Category.TECH_PRODUCTS: DiscordEmoji.TECH_PRODUCTS,
        Category.DEVOPS_CLOUD: DiscordEmoji.DEVOPS_CLOUD,
        Category.OTHER: DiscordEmoji.OTHER,
    }
    return emoji_map.get(category, DiscordEmoji.OTHER)


def get_category_display_name(category: Category, language: SourceLanguage) -> str:
    """Get localized category display name.

    Args:
        category: Article category
        language: Target language (Korean or English)

    Returns:
        Localized category name
    """
    names = {
        Category.AI_ML: {
            SourceLanguage.KOREAN: "AI/머신러닝",
            SourceLanguage.ENGLISH: "AI/ML"
        },
        Category.BLOCKCHAIN_WEB3: {
            SourceLanguage.KOREAN: "블록체인/Web3",
            SourceLanguage.ENGLISH: "Blockchain/Web3"
        },
        Category.STARTUP_BUSINESS: {
            SourceLanguage.KOREAN: "스타트업/비즈니스",
            SourceLanguage.ENGLISH: "Startups/Business"
        },
        Category.TECH_PRODUCTS: {
            SourceLanguage.KOREAN: "테크 제품",
            SourceLanguage.ENGLISH: "Tech Products"
        },
        Category.DEVOPS_CLOUD: {
            SourceLanguage.KOREAN: "DevOps/클라우드",
            SourceLanguage.ENGLISH: "DevOps/Cloud"
        },
        Category.OTHER: {
            SourceLanguage.KOREAN: "기타",
            SourceLanguage.ENGLISH: "Other"
        },
    }

    return names.get(category, {}).get(language, category.value.replace("_", " "))


def format_article_card(article: Article, show_summary: bool = True, max_length: int = 200) -> str:
    """Format an article as a Discord card.

    Args:
        article: Article to format
        show_summary: Whether to include article summary
        max_length: Maximum length for summary (0 to disable)

    Returns:
        Formatted Discord message for the article
    """
    # Get category emoji (use the value, not the enum)
    emoji = get_category_emoji(article.category).value

    # Get language flag (use the value, not the enum)
    lang_flag = (
        DiscordEmoji.KOREAN.value if article.language == SourceLanguage.KOREAN
        else DiscordEmoji.ENGLISH.value
    )

    # Get fresh indicator (use the value, not the enum)
    fresh_indicator = DiscordEmoji.FRESH.value if article.is_fresh(24) else ""

    # Escape title
    title = escape_discord(article.title)

    # Format source
    source = escape_discord(article.source)

    # Format URL
    url = str(article.url)

    # Build card
    card_parts = [
        f"{emoji} **{title}** {lang_flag} {fresh_indicator}",
        f"📎 Source: {source}",
        f"🔗 [Read More]({url})",
    ]

    # Add summary if requested and available
    if show_summary and article.summary:
        summary = article.summary
        if max_length > 0 and len(summary) > max_length:
            summary = summary[:max_length] + "..."
        card_parts.append(f"💬 {escape_discord(summary)}")

    # Add publication time
    if article.published_at:
        pub_date = article.published_at.strftime("%Y-%m-%d %H:%M")
        card_parts.append(f"🕐 Published: {pub_date}")

    # Add tags if available
    if article.tags:
        tags = " ".join(f"`{escape_discord(tag)}`" for tag in article.tags[:5])
        card_parts.append(f"🏷️ {tags}")

    return "\n".join(card_parts)


def format_category_section(
    articles: list[Article],
    category: Category,
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_articles: int = 5
) -> str:
    """Format a category-specific section for Discord.

    Args:
        articles: Articles in this category
        category: Category of this section
        language: Language for section header
        max_articles: Maximum number of articles to include

    Returns:
        Formatted Discord message for the category section
    """
    # Get category emoji (use the value, not the enum)
    emoji = get_category_emoji(category).value
    category_name = get_category_display_name(category, language)

    # Limit articles
    articles = articles[:max_articles]

    # Build section header
    section_parts = [
        f"{emoji} **{category_name}** ({len(articles)} articles)",
        "=" * 50,
    ]

    # Add article cards
    for i, article in enumerate(articles, 1):
        section_parts.append(f"\n### {i}.")
        section_parts.append(format_article_card(article, show_summary=True, max_length=150))

    # Add footer
    section_parts.append(f"\n*{emoji} {category_name} category*")

    return "\n".join(section_parts)


def format_top_stories_section(
    articles: list[Article],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    limit: int = 5
) -> str:
    """Format the Top Stories section for Discord.

    Args:
        articles: Top story articles
        language: Language for section header
        limit: Maximum number of articles

    Returns:
        Formatted Discord message for top stories
    """
    emoji = DiscordEmoji.TOP_STORIES.value
    title = "Top Stories" if language == SourceLanguage.ENGLISH else "주요 뉴스"

    section_parts = [
        f"{emoji} **{title}**",
        "=" * 50,
    ]

    for i, article in enumerate(articles[:limit], 1):
        section_parts.append(f"\n{i}. {format_article_card(article, show_summary=False)}")

    return "\n".join(section_parts)


def format_trending_topics_section(
    keywords: list[tuple[str, int]],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    limit: int = 10
) -> str:
    """Format the Trending Topics section for Discord.

    Args:
        keywords: List of (keyword, count) tuples
        language: Language for section header
        limit: Maximum number of keywords

    Returns:
        Formatted Discord message for trending topics
    """
    emoji = DiscordEmoji.TRENDING_TOPICS.value
    title = "Trending Topics" if language == SourceLanguage.ENGLISH else "트렌딩 토픽"

    section_parts = [
        f"{emoji} **{title}**",
        "=" * 50,
    ]

    for i, (keyword, count) in enumerate(keywords[:limit], 1):
        section_parts.append(f"{i}. `{escape_discord(keyword)}` - {count} mentions")

    return "\n".join(section_parts)


def format_category_breakdown_section(
    category_counts: dict[Category, int],
    total_articles: int,
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> str:
    """Format the Category Breakdown section for Discord.

    Args:
        category_counts: Dictionary mapping categories to counts
        total_articles: Total number of articles
        language: Language for section header

    Returns:
        Formatted Discord message for category breakdown
    """
    emoji = DiscordEmoji.CATEGORY_BREAKDOWN.value
    title = "Category Breakdown" if language == SourceLanguage.ENGLISH else "카테고리 분석"

    section_parts = [
        f"{emoji} **{title}**",
        "=" * 50,
    ]

    # Sort categories by count
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    for category, count in sorted_categories:
        category_emoji = get_category_emoji(category).value
        percentage = (count / total_articles * 100) if total_articles > 0 else 0
        name = get_category_display_name(category, language)
        section_parts.append(
            f"{category_emoji} {name}: **{count}** ({percentage:.1f}%)"
        )

    return "\n".join(section_parts)


def format_most_discussed_section(
    sources: list[tuple[str, int]],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    limit: int = 5
) -> str:
    """Format the Most Discussed section for Discord.

    Args:
        sources: List of (source, count) tuples
        language: Language for section header
        limit: Maximum number of sources

    Returns:
        Formatted Discord message for most discussed sources
    """
    emoji = DiscordEmoji.MOST_DISCUSSED.value
    title = "Most Discussed" if language == SourceLanguage.ENGLISH else "가장 활발한 소스"

    section_parts = [
        f"{emoji} **{title}**",
        "=" * 50,
    ]

    for i, (source, count) in enumerate(sources[:limit], 1):
        section_parts.append(f"{i}. {escape_discord(source)} - {count} articles")

    return "\n".join(section_parts)


def format_editors_picks_section(
    articles: list[Article],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    limit: int = 5
) -> str:
    """Format the Editor's Picks section for Discord.

    Args:
        articles: Selected articles
        language: Language for section header
        limit: Maximum number of articles

    Returns:
        Formatted Discord message for editor's picks
    """
    emoji = DiscordEmoji.EDITORS_PICKS.value
    title = "Editor's Picks" if language == SourceLanguage.ENGLISH else "에디터 추천"

    section_parts = [
        f"{emoji} **{title}**",
        "=" * 50,
    ]

    for i, article in enumerate(articles[:limit], 1):
        section_parts.append(f"\n{i}.")
        section_parts.append(format_article_card(article, show_summary=True, max_length=200))

    return "\n".join(section_parts)


def format_new_this_week_section(
    articles: list[Article],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    limit: int = 8
) -> str:
    """Format the New This Week section for Discord.

    Args:
        articles: Recent articles
        language: Language for section header
        limit: Maximum number of articles

    Returns:
        Formatted Discord message for new articles
    """
    emoji = DiscordEmoji.NEW_THIS_WEEK.value
    title = "New This Week" if language == SourceLanguage.ENGLISH else "이번 주 새 소식"

    section_parts = [
        f"{emoji} **{title}**",
        "=" * 50,
    ]

    for i, article in enumerate(articles[:limit], 1):
        section_parts.append(f"\n{i}. {format_article_card(article, show_summary=False)}")

    return "\n".join(section_parts)


def format_weekly_digest_section(
    articles: list[Article],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    limit: int = 10
) -> str:
    """Format the Weekly Digest section for Discord.

    Args:
        articles: Selected articles for digest
        language: Language for section header
        limit: Maximum number of articles

    Returns:
        Formatted Discord message for weekly digest
    """
    emoji = DiscordEmoji.WEEKLY_DIGEST.value
    title = "Weekly Digest" if language == SourceLanguage.ENGLISH else "주간 다이제스트"

    section_parts = [
        f"{emoji} **{title}**",
        "=" * 50,
    ]

    # Group by category for organized presentation
    category_articles = {}
    for article in articles:
        if article.category not in category_articles:
            category_articles[article.category] = []
        category_articles[article.category].append(article)

    # Display articles grouped by category
    for category, cat_articles in category_articles.items():
        category_emoji = get_category_emoji(category).value
        category_name = get_category_display_name(category, language)

        section_parts.append(f"\n{category_emoji} {category_name}")

        for article in cat_articles[:3]:  # Max 3 per category
            section_parts.append(f"- {escape_discord(article.title)}")

    return "\n".join(section_parts)


def format_full_discord_report(
    aggregation: ReportAggregation,
    language: SourceLanguage = SourceLanguage.ENGLISH,
    include_sections: Optional[list[str]] = None
) -> str:
    """Format a complete Discord weekly report.

    Args:
        aggregation: Report aggregation data
        language: Report language (Korean or English)
        include_sections: List of sections to include (None for all)

    Returns:
        Formatted Discord message for the full report
    """
    # Default sections to include
    if include_sections is None:
        include_sections = [
            "TOP_STORIES",
            "CATEGORY_BREAKDOWN",
            "TRENDING_TOPICS",
            "EDITORS_PICKS",
            "NEW_THIS_WEEK",
        ]

    # Report header
    title = "Tech News Weekly Report" if language == SourceLanguage.ENGLISH else "테크 뉴스 주간 리포트"
    period_start = aggregation.period_start.strftime("%Y-%m-%d")
    period_end = aggregation.period_end.strftime("%Y-%m-%d")

    report_parts = [
        f"# {title}",
        f"**Period:** {period_start} ~ {period_end}",
        f"**Total Articles:** {aggregation.total_articles}",
        "\n" + "=" * 50 + "\n",
    ]

    # Add summary statistics
    korean_count = len(aggregation.by_language.get(SourceLanguage.KOREAN, []))
    english_count = len(aggregation.by_language.get(SourceLanguage.ENGLISH, []))

    report_parts.extend([
        "## 📊 Summary",
        f"{DiscordEmoji.KOREAN.value} Korean: {korean_count} articles",
        f"{DiscordEmoji.ENGLISH.value} English: {english_count} articles",
        "\n" + "-" * 30 + "\n",
    ])

    # Add requested sections
    sections_to_add = {
        "TOP_STORIES": lambda: format_top_stories_section(
            aggregation.sections.get("TOP_STORIES", []),
            language
        ),
        "CATEGORY_BREAKDOWN": lambda: format_category_breakdown_section(
            {cat: stats.count for cat, stats in aggregation.category_stats.items()},
            aggregation.total_articles,
            language
        ),
        "TRENDING_TOPICS": lambda: format_trending_topics_section(
            aggregation.trending_keywords,
            language
        ),
        "MOST_DISCUSSED": lambda: format_most_discussed_section(
            aggregation.top_sources,
            language
        ),
        "EDITORS_PICKS": lambda: format_editors_picks_section(
            aggregation.sections.get("EDITORS_PICKS", []),
            language
        ),
        "NEW_THIS_WEEK": lambda: format_new_this_week_section(
            aggregation.sections.get("NEW_THIS_WEEK", []),
            language
        ),
        "WEEKLY_DIGEST": lambda: format_weekly_digest_section(
            aggregation.sections.get("WEEKLY_DIGEST", []),
            language
        ),
    }

    for section in include_sections:
        if section in sections_to_add:
            report_parts.append("\n" + sections_to_add[section]())

    # Report footer
    footer = (
        "Generated by Ouroboros AI Workflow System"
        if language == SourceLanguage.ENGLISH
        else "Ouroboros AI 워크플로우 시스템에 의해 생성됨"
    )
    report_parts.extend([
        "\n" + "=" * 50,
        f"*{footer}*",
    ])

    return "\n".join(report_parts)


def format_category_report(
    category: Category,
    articles: list[Article],
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> str:
    """Format a category-specific report.

    Args:
        category: Category to report on
        articles: Articles in this category
        language: Report language

    Returns:
        Formatted Discord message for category report
    """
    emoji = get_category_emoji(category).value
    category_name = get_category_display_name(category, language)

    report_text = "Report" if language == SourceLanguage.ENGLISH else "리포트"
    total_text = "Total Articles:" if language == SourceLanguage.ENGLISH else "총 기사:"

    report_parts = [
        f"{emoji} **{category_name} {report_text}**",
        "=" * 50,
        f"**{total_text}** {len(articles)}",
        "\n" + "-" * 30 + "\n",
    ]

    # Add article cards
    for i, article in enumerate(articles[:10], 1):
        report_parts.append(f"\n{i}.")
        report_parts.append(format_article_card(article, show_summary=True, max_length=150))

    return "\n".join(report_parts)


def format_language_report(
    language: SourceLanguage,
    articles: list[Article],
    target_language: SourceLanguage = SourceLanguage.ENGLISH
) -> str:
    """Format a language-specific report.

    Args:
        language: Source language to report on
        articles: Articles in this language
        target_language: Language for report text

    Returns:
        Formatted Discord message for language report
    """
    lang_name = "Korean" if language == SourceLanguage.KOREAN else "English"
    lang_emoji = DiscordEmoji.KOREAN.value if language == SourceLanguage.KOREAN else DiscordEmoji.ENGLISH.value

    title = f"{lang_name} Tech News Report" if target_language == SourceLanguage.ENGLISH else f"{lang_name} 테크 뉴스 리포트"

    report_parts = [
        f"{lang_emoji} **{title}**",
        "=" * 50,
        f"**Total Articles:** {len(articles)}",
        "\n" + "-" * 30 + "\n",
    ]

    # Add article cards
    for i, article in enumerate(articles[:10], 1):
        report_parts.append(f"\n{i}.")
        report_parts.append(format_article_card(article, show_summary=True, max_length=150))

    return "\n".join(report_parts)


# ============================================================================
# INSIGHT FORMATTING FUNCTIONS
# ============================================================================

def get_insight_emoji(insight_category: InsightCategory) -> DiscordEmoji:
    """Get Discord emoji for an insight category.

    Args:
        insight_category: Insight category enum value

    Returns:
        Discord emoji for the insight category
    """
    emoji_map = {
        InsightCategory.HIRING_TRENDS: DiscordEmoji.INSIGHT_HIRING_TRENDS,
        InsightCategory.IN_DEMAND_SKILLS: DiscordEmoji.INSIGHT_IN_DEMAND_SKILLS,
        InsightCategory.COMPANY_NEWS: DiscordEmoji.INSIGHT_COMPANY_NEWS,
        InsightCategory.SALARY_BENEFITS: DiscordEmoji.INSIGHT_SALARY_BENEFITS,
        InsightCategory.CAREER_DEVELOPMENT: DiscordEmoji.INSIGHT_CAREER_DEVELOPMENT,
        InsightCategory.JOB_OPENINGS: DiscordEmoji.INSIGHT_JOB_OPENINGS,
        InsightCategory.INDUSTRY_OUTLOOK: DiscordEmoji.INSIGHT_INDUSTRY_OUTLOOK,
        InsightCategory.TECH_UPDATES: DiscordEmoji.INSIGHT_TECH_UPDATES,
        InsightCategory.WORKPLACE_CULTURE: DiscordEmoji.INSIGHT_WORKPLACE_CULTURE,
        InsightCategory.EDUCATION_TRAINING: DiscordEmoji.INSIGHT_EDUCATION_TRAINING,
        InsightCategory.OTHER: DiscordEmoji.INSIGHT_OTHER,
    }
    return emoji_map.get(insight_category, DiscordEmoji.INSIGHT_OTHER)


def format_skill(skill: ExtractedSkill, show_context: bool = False) -> str:
    """Format a single extracted skill for Discord.

    Args:
        skill: Extracted skill to format
        show_context: Whether to include context snippet

    Returns:
        Formatted Discord message for the skill
    """
    # Get skill level emoji
    level_emojis = {
        "junior": DiscordEmoji.SKILL_JUNIOR,
        "mid": DiscordEmoji.SKILL_MID,
        "senior": DiscordEmoji.SKILL_SENIOR,
        "lead": DiscordEmoji.SKILL_LEAD,
        "principal": DiscordEmoji.SKILL_PRINCIPAL,
        "executive": DiscordEmoji.SKILL_EXECUTIVE,
    }
    level_emoji = level_emojis.get(skill.level.lower(), "")

    # Format skill with relevance score
    relevance_indicator = "🔥" if skill.relevance_score >= 0.7 else "⭐" if skill.relevance_score >= 0.5 else "📌"

    skill_parts = [
        f"{relevance_indicator} `{escape_discord(skill.skill)}` - "
        f"**{skill.category}** {level_emoji.value if level_emoji else ''}",
        f"   Relevance: {skill.relevance_score:.2f}",
    ]

    # Add context if requested
    if show_context and skill.context:
        context = skill.context[:100] + "..." if len(skill.context) > 100 else skill.context
        skill_parts.append(f"   Context: *{escape_discord(context)}*")

    return "\n".join(skill_parts)


def format_skills_section(
    skills: list[ExtractedSkill],
    title: str = "In-Demand Skills",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_skills: int = 10
) -> str:
    """Format a section displaying extracted skills.

    Args:
        skills: List of extracted skills
        title: Section title
        language: Report language
        max_skills: Maximum number of skills to display

    Returns:
        Formatted Discord message for skills section
    """
    emoji = DiscordEmoji.INSIGHT_IN_DEMAND_SKILLS.value
    title_korean = "필요 스킬" if language == SourceLanguage.KOREAN else title

    section_parts = [
        f"{emoji} **{title_korean}**",
        "=" * 50,
    ]

    if not skills:
        section_parts.append("*No skills extracted*")
        return "\n".join(section_parts)

    # Sort by relevance score
    sorted_skills = sorted(skills, key=lambda x: x.relevance_score, reverse=True)

    for i, skill in enumerate(sorted_skills[:max_skills], 1):
        skill_text = format_skill(skill, show_context=False)
        section_parts.append(f"\n{i}. {skill_text}")

    return "\n".join(section_parts)


def format_company(company: ExtractedCompany, show_context: bool = False) -> str:
    """Format a single extracted company for Discord.

    Args:
        company: Extracted company to format
        show_context: Whether to include context snippet

    Returns:
        Formatted Discord message for the company
    """
    # Get action emoji
    action_emojis = {
        "hiring": DiscordEmoji.COMPANY_HIRING,
        "funding": DiscordEmoji.COMPANY_FUNDING,
        "acquisition": DiscordEmoji.COMPANY_ACQUISITION,
        "expansion": DiscordEmoji.COMPANY_EXPANSION,
        "ipo": DiscordEmoji.COMPANY_IPO,
        "layoff": DiscordEmoji.COMPANY_LAYOFF,
        "launch": DiscordEmoji.COMPANY_LAUNCH,
    }
    action_emoji = action_emojis.get(company.action.lower(), "🏢")

    company_parts = [
        f"{action_emoji.value} **{escape_discord(company.name)}** - *{company.action}*",
    ]

    # Add metrics if available
    if company.metrics:
        metrics_text = ", ".join(f"{k}: {v}" for k, v in company.metrics.items())
        company_parts.append(f"   📊 {metrics_text}")

    # Add context if requested
    if show_context and company.context:
        context = company.context[:100] + "..." if len(company.context) > 100 else company.context
        company_parts.append(f"   Context: *{escape_discord(context)}*")

    return "\n".join(company_parts)


def format_companies_section(
    companies: list[ExtractedCompany],
    title: str = "Company News",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_companies: int = 8
) -> str:
    """Format a section displaying extracted companies.

    Args:
        companies: List of extracted companies
        title: Section title
        language: Report language
        max_companies: Maximum number of companies to display

    Returns:
        Formatted Discord message for companies section
    """
    emoji = DiscordEmoji.INSIGHT_COMPANY_NEWS.value
    title_korean = "기업 뉴스" if language == SourceLanguage.KOREAN else title

    section_parts = [
        f"{emoji} **{title_korean}**",
        "=" * 50,
    ]

    if not companies:
        section_parts.append("*No companies extracted*")
        return "\n".join(section_parts)

    # Sort by action type priority
    action_priority = {
        "hiring": 1,
        "funding": 2,
        "ipo": 3,
        "acquisition": 4,
        "expansion": 5,
        "launch": 6,
        "layoff": 7,
    }
    sorted_companies = sorted(
        companies,
        key=lambda x: action_priority.get(x.action.lower(), 99)
    )

    for i, company in enumerate(sorted_companies[:max_companies], 1):
        company_text = format_company(company, show_context=False)
        section_parts.append(f"\n{i}. {company_text}")

    return "\n".join(section_parts)


def format_salary(salary: ExtractedSalary, show_context: bool = False) -> str:
    """Format a single extracted salary for Discord.

    Args:
        salary: Extracted salary to format
        show_context: Whether to include context snippet

    Returns:
        Formatted Discord message for the salary
    """
    salary_parts = [
        f"💰 **{salary.currency} {salary.amount_min} - {salary.amount_max}**",
        f"   Period: *{salary.period}*",
    ]

    # Add role if available
    if salary.role:
        salary_parts.append(f"   Role: `{escape_discord(salary.role)}`")

    # Add context if requested
    if show_context and salary.context:
        context = salary.context[:100] + "..." if len(salary.context) > 100 else salary.context
        salary_parts.append(f"   Context: *{escape_discord(context)}*")

    return "\n".join(salary_parts)


def format_salaries_section(
    salaries: list[ExtractedSalary],
    title: str = "Salary Information",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_salaries: int = 6
) -> str:
    """Format a section displaying extracted salaries.

    Args:
        salaries: List of extracted salaries
        title: Section title
        language: Report language
        max_salaries: Maximum number of salaries to display

    Returns:
        Formatted Discord message for salaries section
    """
    emoji = DiscordEmoji.INSIGHT_SALARY_BENEFITS.value
    title_korean = "연봉 정보" if language == SourceLanguage.KOREAN else title

    section_parts = [
        f"{emoji} **{title_korean}**",
        "=" * 50,
    ]

    if not salaries:
        section_parts.append("*No salary information extracted*")
        return "\n".join(section_parts)

    # Sort by maximum salary (descending)
    sorted_salaries = sorted(salaries, key=lambda x: x.amount_max or 0, reverse=True)

    for i, salary in enumerate(sorted_salaries[:max_salaries], 1):
        salary_text = format_salary(salary, show_context=False)
        section_parts.append(f"\n{i}. {salary_text}")

    return "\n".join(section_parts)


def format_job_title(job_title: ExtractedJobTitle, show_context: bool = False) -> str:
    """Format a single extracted job title for Discord.

    Args:
        job_title: Extracted job title to format
        show_context: Whether to include context snippet

    Returns:
        Formatted Discord message for the job title
    """
    title_parts = [
        f"🎯 **{escape_discord(job_title.title)}**",
        f"   Level: *{str(job_title.level)}*",
    ]

    # Add company if available
    if job_title.company:
        title_parts.append(f"   Company: `{escape_discord(job_title.company)}`")

    # Add location if available
    if job_title.location:
        title_parts.append(f"   Location: `{escape_discord(job_title.location)}`")

    # Add position count if available
    if job_title.count:
        title_parts.append(f"   Positions: **{job_title.count}**")

    # Add context if requested
    if show_context and job_title.context:
        context = job_title.context[:100] + "..." if len(job_title.context) > 100 else job_title.context
        title_parts.append(f"   Context: *{escape_discord(context)}*")

    return "\n".join(title_parts)


def format_job_titles_section(
    job_titles: list[ExtractedJobTitle],
    title: str = "Job Openings",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_titles: int = 8
) -> str:
    """Format a section displaying extracted job titles.

    Args:
        job_titles: List of extracted job titles
        title: Section title
        language: Report language
        max_titles: Maximum number of job titles to display

    Returns:
        Formatted Discord message for job titles section
    """
    emoji = DiscordEmoji.INSIGHT_JOB_OPENINGS.value
    title_korean = "채용 공고" if language == SourceLanguage.KOREAN else title

    section_parts = [
        f"{emoji} **{title_korean}**",
        "=" * 50,
    ]

    if not job_titles:
        section_parts.append("*No job titles extracted*")
        return "\n".join(section_parts)

    # Sort by position count (descending)
    sorted_titles = sorted(job_titles, key=lambda x: x.count or 0, reverse=True)

    for i, job_title in enumerate(sorted_titles[:max_titles], 1):
        title_text = format_job_title(job_title, show_context=False)
        section_parts.append(f"\n{i}. {title_text}")

    return "\n".join(section_parts)


def format_location(location: ExtractedLocation, show_context: bool = False) -> str:
    """Format a single extracted location for Discord.

    Args:
        location: Extracted location to format
        show_context: Whether to include context snippet

    Returns:
        Formatted Discord message for the location
    """
    # Get location emoji based on type
    location_emojis = {
        "city": DiscordEmoji.LOCATION_CITY,
        "country": DiscordEmoji.LOCATION_COUNTRY,
        "remote": DiscordEmoji.LOCATION_REMOTE,
    }
    location_emoji = location_emojis.get(location.type.lower(), "📍")

    location_parts = [
        f"{location_emoji.value} **{escape_discord(location.location)}**",
        f"   Type: *{location.type}*",
    ]

    # Add context if requested
    if show_context and location.context:
        context = location.context[:100] + "..." if len(location.context) > 100 else location.context
        location_parts.append(f"   Context: *{escape_discord(context)}*")

    return "\n".join(location_parts)


def format_locations_section(
    locations: list[ExtractedLocation],
    title: str = "Job Locations",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_locations: int = 6
) -> str:
    """Format a section displaying extracted locations.

    Args:
        locations: List of extracted locations
        title: Section title
        language: Report language
        max_locations: Maximum number of locations to display

    Returns:
        Formatted Discord message for locations section
    """
    emoji = DiscordEmoji.INSIGHT_JOB_OPENINGS.value
    title_korean = "채용 위치" if language == SourceLanguage.KOREAN else title

    section_parts = [
        f"{emoji} **{title_korean}**",
        "=" * 50,
    ]

    if not locations:
        section_parts.append("*No locations extracted*")
        return "\n".join(section_parts)

    # Sort by type (remote first, then cities, then countries)
    type_priority = {"remote": 1, "city": 2, "country": 3}
    sorted_locations = sorted(
        locations,
        key=lambda x: type_priority.get(x.type.lower(), 99)
    )

    for i, location in enumerate(sorted_locations[:max_locations], 1):
        location_text = format_location(location, show_context=False)
        section_parts.append(f"\n{i}. {location_text}")

    return "\n".join(section_parts)


def format_key_takeaways_section(
    takeaways: list[tuple[str, float]],
    title: str = "Key Takeaways",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_takeaways: int = 5
) -> str:
    """Format a section displaying key takeaways.

    Args:
        takeaways: List of (takeaway_text, relevance_score) tuples
        title: Section title
        language: Report language
        max_takeaways: Maximum number of takeaways to display

    Returns:
        Formatted Discord message for key takeaways section
    """
    emoji = "💡"
    title_korean = "핵심 내용" if language == SourceLanguage.KOREAN else title

    section_parts = [
        f"{emoji} **{title_korean}**",
        "=" * 50,
    ]

    if not takeaways:
        section_parts.append("*No key takeaways extracted*")
        return "\n".join(section_parts)

    # Sort by relevance score
    sorted_takeaways = sorted(takeaways, key=lambda x: x[1], reverse=True)

    for i, (takeaway, score) in enumerate(sorted_takeaways[:max_takeaways], 1):
        relevance = "🔥" if score >= 0.8 else "⭐" if score >= 0.6 else "📌"
        section_parts.append(f"\n{i}. {relevance} {escape_discord(takeaway)}")
        section_parts.append(f"   Relevance: {score:.2f}")

    return "\n".join(section_parts)


def format_insight_report(
    insight: ExtractedInsight,
    article_title: str = "Article",
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> str:
    """Format a comprehensive insight report for a single article.

    Args:
        insight: Extracted insights object
        article_title: Title of the article
        language: Report language

    Returns:
        Formatted Discord message for insight report
    """
    report_header = f"**{escape_discord(article_title)}** - Insights Report"
    if language == SourceLanguage.KOREAN:
        report_header = f"**{escape_discord(article_title)}** - 인사이트 리포트"

    report_parts = [
        report_header,
        "=" * 50,
    ]

    # Add each insight type if present
    if insight.skills:
        report_parts.append("\n" + format_skills_section(
            insight.skills[:5],
            title="Top Skills",
            language=language,
            max_skills=5
        ))

    if insight.companies:
        report_parts.append("\n" + format_companies_section(
            insight.companies[:5],
            title="Companies",
            language=language,
            max_companies=5
        ))

    if insight.salaries:
        report_parts.append("\n" + format_salaries_section(
            insight.salaries[:3],
            title="Salaries",
            language=language,
            max_salaries=3
        ))

    if insight.job_titles:
        report_parts.append("\n" + format_job_titles_section(
            insight.job_titles[:5],
            title="Job Titles",
            language=language,
            max_titles=5
        ))

    if insight.locations:
        report_parts.append("\n" + format_locations_section(
            insight.locations[:4],
            title="Locations",
            language=language,
            max_locations=4
        ))

    if insight.key_takeaways:
        # Convert takeaways to tuples with scores
        takeaways_with_scores = [
            (t, getattr(t, 'relevance_score', 0.5))
            for t in insight.key_takeaways
        ]
        report_parts.append("\n" + format_key_takeaways_section(
            takeaways_with_scores[:3],
            title="Key Takeaways",
            language=language,
            max_takeaways=3
        ))

    if not any([insight.skills, insight.companies, insight.salaries,
                insight.job_titles, insight.locations, insight.key_takeaways]):
        report_parts.append("\n*No insights extracted from this article*")

    return "\n".join(report_parts)


def format_weekly_insights_report(
    articles_insights: list[tuple[Article, ExtractedInsight]],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_articles: int = 5
) -> str:
    """Format a weekly insights report from multiple articles.

    Args:
        articles_insights: List of (article, insights) tuples
        language: Report language
        max_articles: Maximum number of articles to include

    Returns:
        Formatted Discord message for weekly insights report
    """
    title = "Weekly Insights Report" if language == SourceLanguage.ENGLISH else "주간 인사이트 리포트"

    report_parts = [
        f"# {title}",
        f"**{len(articles_insights)} articles analyzed**",
        "\n" + "=" * 50 + "\n",
    ]

    # Aggregate insights across all articles
    all_skills = []
    all_companies = []
    all_salaries = []
    all_job_titles = []
    all_locations = []
    all_takeaways = []

    for article, insight in articles_insights:
        if insight.skills:
            all_skills.extend(insight.skills)
        if insight.companies:
            all_companies.extend(insight.companies)
        if insight.salaries:
            all_salaries.extend(insight.salaries)
        if insight.job_titles:
            all_job_titles.extend(insight.job_titles)
        if insight.locations:
            all_locations.extend(insight.locations)
        if insight.key_takeaways:
            all_takeaways.extend(insight.key_takeaways)

    # Add summary statistics
    report_parts.append("## 📊 Summary")
    report_parts.append(f"💡 Skills Extracted: {len(all_skills)}")
    report_parts.append(f"🏢 Companies: {len(all_companies)}")
    report_parts.append(f"💰 Salary Data: {len(all_salaries)}")
    report_parts.append(f"🎯 Job Titles: {len(all_job_titles)}")
    report_parts.append(f"📍 Locations: {len(all_locations)}")
    report_parts.append(f"✨ Key Takeaways: {len(all_takeaways)}")
    report_parts.append("\n" + "-" * 30 + "\n")

    # Add top insights by category
    if all_skills:
        report_parts.append("\n" + format_skills_section(
            all_skills[:10],
            title="Top Skills This Week",
            language=language,
            max_skills=10
        ))

    if all_companies:
        report_parts.append("\n" + format_companies_section(
            all_companies[:8],
            title="Top Companies",
            language=language,
            max_companies=8
        ))

    if all_salaries:
        report_parts.append("\n" + format_salaries_section(
            all_salaries[:6],
            title="Salary Highlights",
            language=language,
            max_salaries=6
        ))

    if all_job_titles:
        report_parts.append("\n" + format_job_titles_section(
            all_job_titles[:8],
            title="Job Opportunities",
            language=language,
            max_titles=8
        ))

    # Add article-level insights for top articles
    if max_articles > 0:
        report_parts.append("\n## 📰 Top Articles with Insights")
        report_parts.append("=" * 50)

        for i, (article, insight) in enumerate(articles_insights[:max_articles], 1):
            # Only include articles with insights
            if any([insight.skills, insight.companies, insight.salaries,
                    insight.job_titles, insight.locations, insight.key_takeaways]):
                report_parts.append(f"\n### {i}. {escape_discord(article.title)}")
                report_parts.append(f"🔗 {article.url}")
                report_parts.append(f"📂 Category: {article.category.value}")

                # Add insight summary
                insight_types = []
                if insight.skills:
                    insight_types.append(f"{len(insight.skills)} skills")
                if insight.companies:
                    insight_types.append(f"{len(insight.companies)} companies")
                if insight.salaries:
                    insight_types.append(f"{len(insight.salaries)} salary data")
                if insight.job_titles:
                    insight_types.append(f"{len(insight.job_titles)} job titles")
                if insight.locations:
                    insight_types.append(f"{len(insight.locations)} locations")
                if insight.key_takeaways:
                    insight_types.append(f"{len(insight.key_takeaways)} takeaways")

                report_parts.append(f"💡 Insights: {', '.join(insight_types)}")

    return "\n".join(report_parts)


# Export public API
__all__ = [
    "escape_discord",
    "DiscordEmoji",
    "CategoryTemplate",
    "SectionTemplate",
    "get_category_emoji",
    "get_category_display_name",
    "format_article_card",
    "format_category_section",
    "format_top_stories_section",
    "format_trending_topics_section",
    "format_category_breakdown_section",
    "format_most_discussed_section",
    "format_editors_picks_section",
    "format_new_this_week_section",
    "format_weekly_digest_section",
    "format_full_discord_report",
    "format_category_report",
    "format_language_report",
    # Insight formatting functions
    "get_insight_emoji",
    "format_skill",
    "format_skills_section",
    "format_company",
    "format_companies_section",
    "format_salary",
    "format_salaries_section",
    "format_job_title",
    "format_job_titles_section",
    "format_location",
    "format_locations_section",
    "format_key_takeaways_section",
    "format_insight_report",
    "format_weekly_insights_report",
]
