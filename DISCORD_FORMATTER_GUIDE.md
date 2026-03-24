# Discord Formatter Guide

## Overview

The Discord formatter module (`discord_formatter.py`) provides comprehensive message formatting templates for displaying crawled tech news articles in Discord. It supports bilingual formatting (Korean and English), category-specific styling, and Discord-optimized markdown rendering.

## Features

- ✅ **Category-Specific Templates** - Unique formatting for each of 5 categories
- ✅ **Bilingual Support** - Full Korean and English language support
- ✅ **Discord Markdown Optimization** - Escaped special characters, proper formatting
- ✅ **Emoji-Enhanced Presentation** - Visual categorization with Discord-compatible emojis
- ✅ **Flexible Report Sections** - Multiple section types for different use cases
- ✅ **Comprehensive Test Coverage** - 61 passing unit tests

## Installation

The Discord formatter is part of the Ouroboros crawler module. No additional installation is required.

```python
from ouroboros.crawler.discord_formatter import (
    format_article_card,
    format_category_section,
    format_full_discord_report,
    # ... and more
)
```

## Core Concepts

### Emojis

The module uses Discord-compatible emojis for visual categorization:

| Type | Emoji | Description |
|------|-------|-------------|
| AI/ML | 🤖 | AI and Machine Learning |
| Blockchain/Web3 | ⛓️ | Blockchain and Web3 technologies |
| Startups/Business | 🚀 | Startups and Business news |
| Tech Products | 📱 | Technology products |
| DevOps/Cloud | ☁️ | DevOps and Cloud computing |
| Other | 📰 | Other categories |

### Section Emojis

| Section | Emoji | Description |
|---------|-------|-------------|
| Top Stories | 🔥 | Most important articles |
| Trending Topics | 📈 | Hot topics and keywords |
| Category Breakdown | 📊 | Statistics by category |
| Most Discussed | 💬 | Most active sources |
| Editor's Picks | ⭐ | Curated in-depth articles |
| New This Week | ✨ | Latest articles |
| Weekly Digest | 📋 | Comprehensive overview |

### Status Emojis

| Status | Emoji | Description |
|--------|-------|-------------|
| Korean | 🇰🇷 | Korean language content |
| English | 🇺🇸 | English language content |
| Fresh | 🆕 | Published within 24 hours |
| Breaking | 🚨 | Breaking news |
| High Priority | ⬆️ | High priority content |
| Low Priority | ⬇️ | Low priority content |

## Usage Examples

### 1. Format a Single Article Card

```python
from ouroboros.crawler.discord_formatter import format_article_card
from ouroboros.crawler.models import SourceLanguage

# Basic article card
card = format_article_card(article)
print(card)

# Article card without summary
card = format_article_card(article, show_summary=False)

# Article card with custom summary length
card = format_article_card(article, show_summary=True, max_length=150)
```

**Output Example:**
```
🤖 **AI Model Breakthrough Achieves 99% Accuracy** 🇺🇸 🆕
📎 Source: TechCrunch
🔗 [Read More](https://techcrunch.com/article)
💬 Researchers have achieved a breakthrough in AI models...
🕐 Published: 2026-03-24 10:30
🏷️ `ai` `machine learning` `breakthrough`
```

### 2. Format a Category Section

```python
from ouroboros.crawler.discord_formatter import format_category_section
from ouroboros.crawler.models import Category, SourceLanguage

# English category section
section = format_category_section(
    articles=ai_articles,
    category=Category.AI_ML,
    language=SourceLanguage.ENGLISH,
    max_articles=5
)

# Korean category section
section = format_category_section(
    articles=ai_articles,
    category=Category.AI_ML,
    language=SourceLanguage.KOREAN,
    max_articles=5
)
```

**Output Example (English):**
```
🤖 **AI/ML** (45 articles)
==================================================

### 1.
🤖 **AI Model Breakthrough** 🇺🇸 🆕
📎 Source: TechCrunch
🔗 [Read More](https://techcrunch.com/article)
💬 Summary...
🕐 Published: 2026-03-24 10:30

### 2.
...

*🤖 AI/ML category*
```

### 3. Format Top Stories Section

```python
from ouroboros.crawler.discord_formatter import format_top_stories_section
from ouroboros.crawler.models import SourceLanguage

# English top stories
section = format_top_stories_section(articles, SourceLanguage.ENGLISH, limit=10)

# Korean top stories
section = format_top_stories_section(articles, SourceLanguage.KOREAN, limit=10)
```

### 4. Format Trending Topics

```python
from ouroboros.crawler.discord_formatter import format_trending_topics_section
from ouroboros.crawler.models import SourceLanguage

keywords = [("ai", 50), ("startup", 45), ("blockchain", 30)]

section = format_trending_topics_section(keywords, SourceLanguage.ENGLISH)
```

**Output Example:**
```
📈 **Trending Topics**
==================================================
1. `ai` - 50 mentions
2. `startup` - 45 mentions
3. `blockchain` - 30 mentions
```

### 5. Format Category Breakdown

```python
from ouroboros.crawler.discord_formatter import format_category_breakdown_section
from ouroboros.crawler.models import Category, SourceLanguage

category_counts = {
    Category.AI_ML: 45,
    Category.STARTUP_BUSINESS: 30,
    Category.BLOCKCHAIN_WEB3: 25,
}

section = format_category_breakdown_section(
    category_counts,
    total_articles=100,
    language=SourceLanguage.ENGLISH
)
```

**Output Example:**
```
📊 **Category Breakdown**
==================================================
🤖 AI/ML: **45** (45.0%)
🚀 Startups/Business: **30** (30.0%)
⛓️ Blockchain/Web3: **25** (25.0%)
```

### 6. Format Full Discord Report

```python
from ouroboros.crawler.discord_formatter import format_full_discord_report
from ouroboros.crawler.report_categorization import categorize_for_report
from ouroboros.crawler.models import SourceLanguage

# Categorize articles for report
aggregation = categorize_for_report(
    articles=articles,
    period_start=datetime.now() - timedelta(days=7),
    period_end=datetime.now()
)

# Generate full Discord report (English)
report = format_full_discord_report(aggregation, SourceLanguage.ENGLISH)

# Generate full Discord report (Korean)
report = format_full_discord_report(aggregation, SourceLanguage.KOREAN)

# Generate report with custom sections
report = format_full_discord_report(
    aggregation,
    SourceLanguage.ENGLISH,
    include_sections=["TOP_STORIES", "CATEGORY_BREAKDOWN", "TRENDING_TOPICS"]
)
```

**Output Example:**
```
# Tech News Weekly Report
**Period:** 2026-03-17 ~ 2026-03-24
**Total Articles:** 150

==================================================

## 📊 Summary
🇰🇷 Korean: 65 articles
🇺🇸 English: 85 articles

------------------------------

## 🔥 Top Stories
1. 🤖 **AI Model Breakthrough** 🇺🇸 🆕
📎 Source: TechCrunch
🔗 [Read More](https://techcrunch.com/article)

2. 🚀 **Startup Raises $100M** 🇺🇸
...

## 📊 Category Breakdown
🤖 AI/ML: **45** (45.0%)
🚀 Startups/Business: **30** (30.0%)
...

## 📈 Trending Topics
1. `ai` - 50 mentions
2. `startup` - 45 mentions
...

==================================================
*Generated by Ouroboros AI Workflow System*
```

### 7. Format Category-Specific Report

```python
from ouroboros.crawler.discord_formatter import format_category_report
from ouroboros.crawler.models import Category, SourceLanguage

# AI/ML report in English
report = format_category_report(
    category=Category.AI_ML,
    articles=ai_articles,
    language=SourceLanguage.ENGLISH
)

# AI/ML report in Korean
report = format_category_report(
    category=Category.AI_ML,
    articles=ai_articles,
    language=SourceLanguage.KOREAN
)
```

### 8. Format Language-Specific Report

```python
from ouroboros.crawler.discord_formatter import format_language_report
from ouroboros.crawler.models import SourceLanguage

# English articles report
english_articles = [a for a in articles if a.language == SourceLanguage.ENGLISH]
report = format_language_report(
    language=SourceLanguage.ENGLISH,
    articles=english_articles,
    target_language=SourceLanguage.ENGLISH
)

# Korean articles report (in Korean)
korean_articles = [a for a in articles if a.language == SourceLanguage.KOREAN]
report = format_language_report(
    language=SourceLanguage.KOREAN,
    articles=korean_articles,
    target_language=SourceLanguage.KOREAN
)
```

## Category Display Names

The module provides localized category display names:

| Category | English | Korean |
|----------|---------|--------|
| AI_ML | AI/ML | AI/머신러닝 |
| BLOCKCHAIN_WEB3 | Blockchain/Web3 | 블록체인/Web3 |
| STARTUP_BUSINESS | Startups/Business | 스타트업/비즈니스 |
| TECH_PRODUCTS | Tech Products | 테크 제품 |
| DEVOPS_CLOUD | DevOps/Cloud | DevOps/클라우드 |
| OTHER | Other | 기타 |

## Discord Markdown Safety

All text is properly escaped for Discord markdown:

```python
from ouroboros.crawler.discord_formatter import escape_discord

# Escapes special Discord characters
text = "This is *bold* and _italic_ text"
safe_text = escape_discord(text)
# Result: "This is \*bold\* and \_italic\_ text"
```

**Escaped Characters:**
- `\` → `\\`
- `*` → `\*`
- `_` → `\_`
- `~` → `\~`
- `|` → `\|`
- `` ` `` → `` \` ``
- `>` → `\>`

## API Reference

### Core Functions

#### `format_article_card(article, show_summary=True, max_length=200)`
Format an article as a Discord card.

**Parameters:**
- `article`: Article to format
- `show_summary`: Whether to include article summary (default: True)
- `max_length`: Maximum length for summary (default: 200, 0 to disable)

**Returns:** Formatted Discord message string

#### `format_category_section(articles, category, language=SourceLanguage.ENGLISH, max_articles=5)`
Format a category-specific section.

**Parameters:**
- `articles`: Articles in this category
- `category`: Category of this section
- `language`: Language for section header (default: English)
- `max_articles`: Maximum number of articles (default: 5)

**Returns:** Formatted Discord message string

#### `format_full_discord_report(aggregation, language=SourceLanguage.ENGLISH, include_sections=None)`
Format a complete Discord weekly report.

**Parameters:**
- `aggregation`: ReportAggregation object with categorized data
- `language`: Report language (default: English)
- `include_sections`: List of sections to include (default: all)

**Returns:** Formatted Discord message string

#### `format_category_report(category, articles, language=SourceLanguage.ENGLISH)`
Format a category-specific report.

**Parameters:**
- `category`: Category to report on
- `articles`: Articles in this category
- `language`: Report language (default: English)

**Returns:** Formatted Discord message string

#### `format_language_report(language, articles, target_language=SourceLanguage.ENGLISH)`
Format a language-specific report.

**Parameters:**
- `language`: Source language to report on
- `articles`: Articles in this language
- `target_language`: Language for report text (default: English)

**Returns:** Formatted Discord message string

### Section Formatters

#### `format_top_stories_section(articles, language=SourceLanguage.ENGLISH, limit=5)`
Format the Top Stories section.

#### `format_trending_topics_section(keywords, language=SourceLanguage.ENGLISH, limit=10)`
Format the Trending Topics section.

#### `format_category_breakdown_section(category_counts, total_articles, language=SourceLanguage.ENGLISH)`
Format the Category Breakdown section.

#### `format_most_discussed_section(sources, language=SourceLanguage.ENGLISH, limit=5)`
Format the Most Discussed section.

#### `format_editors_picks_section(articles, language=SourceLanguage.ENGLISH, limit=5)`
Format the Editor's Picks section.

#### `format_new_this_week_section(articles, language=SourceLanguage.ENGLISH, limit=8)`
Format the New This Week section.

#### `format_weekly_digest_section(articles, language=SourceLanguage.ENGLISH, limit=10)`
Format the Weekly Digest section.

### Helper Functions

#### `escape_discord(text)`
Escape Discord markdown special characters.

#### `get_category_emoji(category)`
Get Discord emoji for a category.

#### `get_category_display_name(category, language)`
Get localized category display name.

## Discord Message Limits

Discord has the following message limits:
- **Maximum message length**: 2000 characters
- **Maximum embeds per message**: 10
- **Maximum fields per embed**: 25

**Best Practices:**
- Use section formatters for longer content
- Split reports into multiple messages if needed
- Limit article summaries to keep messages concise

## Integration with Discord Webhooks

```python
import requests
from ouroboros.crawler.discord_formatter import format_full_discord_report
from ouroboros.crawler.report_categorization import categorize_for_report

# Generate report
aggregation = categorize_for_report(articles, period_start, period_end)
discord_report = format_full_discord_report(aggregation)

# Send to Discord webhook
webhook_url = "https://discord.com/api/webhooks/..."
payload = {"content": discord_report}
response = requests.post(webhook_url, json=payload)
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/unit/crawler/test_discord_formatter.py -v
```

**Test Coverage:** 61 tests, 100% passing

Test categories:
- Discord markdown escaping (7 tests)
- Emoji enums (3 tests)
- Category emoji mapping (6 tests)
- Category display names (10 tests)
- Article card formatting (6 tests)
- Category section formatting (3 tests)
- Section formatting (15 tests)
- Full report formatting (3 tests)
- Category report formatting (2 tests)
- Language report formatting (2 tests)
- Trending topics formatting (3 tests)
- Category breakdown formatting (2 tests)
- Most discussed formatting (2 tests)

## Examples

### Example 1: Daily Summary

```python
from datetime import datetime, timedelta
from ouroboros.crawler.discord_formatter import (
    format_top_stories_section,
    format_trending_topics_section,
)
from ouroboros.crawler.models import SourceLanguage

# Get today's articles
today = datetime.now().date()
daily_articles = [a for a in articles if a.published_at.date() == today]

# Generate daily summary
summary = f"# Daily Tech News Summary - {today}\n\n"
summary += format_top_stories_section(daily_articles[:5], SourceLanguage.ENGLISH)
summary += "\n\n"
summary += format_trending_topics_section(trending_keywords[:10], SourceLanguage.ENGLISH)

# Send to Discord
send_to_discord(summary)
```

### Example 2: Category Alert

```python
from ouroboros.crawler.discord_formatter import format_category_report
from ouroboros.crawler.models import Category, SourceLanguage

# Get AI/ML articles from last 24 hours
recent_ai = [
    a for a in articles
    if a.category == Category.AI_ML and a.is_fresh(24)
]

# Generate AI/ML alert
alert = "🚨 **AI/ML Breaking News Alert!**\n\n"
alert += format_category_report(Category.AI_ML, recent_ai, SourceLanguage.ENGLISH)

# Send to Discord
send_to_discord(alert)
```

### Example 3: Bilingual Report

```python
from ouroboros.crawler.discord_formatter import format_full_discord_report
from ouroboros.crawler.models import SourceLanguage

# Generate English report
english_report = format_full_discord_report(aggregation, SourceLanguage.ENGLISH)
send_to_discord(english_report)

# Generate Korean report
korean_report = format_full_discord_report(aggregation, SourceLanguage.KOREAN)
send_to_discord(korean_report)
```

## Best Practices

1. **Always escape user input** before formatting
   ```python
   title = escape_discord(user_input_title)
   ```

2. **Use appropriate section limits** to avoid Discord message length limits
   ```python
   # Good: Reasonable limits
   section = format_top_stories_section(articles, limit=10)

   # Bad: Too many articles
   section = format_top_stories_section(articles, limit=100)
   ```

3. **Check for empty results** before formatting
   ```python
   if not articles:
       return "No articles found for this period."
   ```

4. **Use language parameter** consistently
   ```python
   # Good: Consistent language
   report = format_full_discord_report(aggregation, SourceLanguage.KOREAN)

   # Bad: Mixed languages
   report_korean = format_top_stories_section(articles, SourceLanguage.KOREAN)
   report_english = format_category_breakdown_section(counts, SourceLanguage.ENGLISH)
   ```

5. **Customize article display** based on use case
   ```python
   # For quick summaries: Hide summaries
   quick_card = format_article_card(article, show_summary=False)

   # For detailed reports: Include summaries
   detailed_card = format_article_card(article, show_summary=True, max_length=300)
   ```

## Troubleshooting

### Issue: Messages too long for Discord
**Solution:** Split reports into multiple messages or use fewer articles per section.

```python
# Instead of 20 articles, use 10
section = format_top_stories_section(articles, limit=10)
```

### Issue: Emojis not displaying correctly
**Solution:** Ensure you're using Discord-compatible emojis from the `DiscordEmoji` enum.

```python
# Good: Use enum value
emoji = DiscordEmoji.AI_ML.value

# Bad: Custom emoji
emoji = "😊"  # May not work in all Discord clients
```

### Issue: Korean text not displaying properly
**Solution:** Ensure UTF-8 encoding when sending to Discord.

```python
import requests

response = requests.post(
    webhook_url,
    json={"content": korean_report},
    headers={"Content-Type": "application/json; charset=utf-8"}
)
```

## Related Documentation

- [README.md](README.md) - Main crawler documentation
- [REPORT_CATEGORIZATION_GUIDE.md](REPORT_CATEGORIZATION_GUIDE.md) - Report categorization system
- [models.py](models.py) - Article and category data models
- [classification.py](classification.py) - Article classification

## License

Part of the Ouroboros AI Workflow System project.
