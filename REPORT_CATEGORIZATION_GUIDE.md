# Report Categorization System for Discord Weekly Reports

## Overview

The report categorization system provides a comprehensive framework for organizing crawled tech news articles into structured weekly Discord reports. This system aggregates articles from the 30-site crawler and categorizes them into meaningful sections for presentation.

## Purpose

While the individual article classification system (5 categories: AI_ML, BLOCKCHAIN_WEB3, STARTUP_BUSINESS, TECH_PRODUCTS, DEVOPS_CLOUD) categorizes articles by topic, the report categorization system organizes articles for **report presentation and summary**.

## Key Components

### 1. Report Sections

Articles are organized into the following report sections:

| Section | Description | Purpose |
|----------|-------------|---------|
| **TOP_STORIES** | Top 10 most important articles overall | Main highlights of the week |
| **TRENDING_TOPICS** | Articles related to trending keywords | Focus on hot topics |
| **MOST_DISCUSSED** | Articles from most active sources | Highlight active sources |
| **EDITORS_PICKS** | Longest, in-depth articles | Deep-dive content |
| **NEW_THIS_WEEK** | Most recently published articles | Latest developments |
| **WEEKLY_DIGEST** | Balanced selection from each category | Comprehensive overview |

### 2. Article Scoring & Prioritization

Articles are scored based on multiple factors:

#### Scoring Factors

1. **Content Length** (Max: 5.0 points)
   - Longer articles get higher scores
   - Indicates in-depth coverage
   - Formula: `min(len(content) / 1000, 5)`

2. **Category Weight** (Multiplier: 0.8 - 1.5)
   - AI_ML: 1.5 (highest importance)
   - STARTUP_BUSINESS: 1.3
   - BLOCKCHAIN_WEB3: 1.2
   - DEVOPS_CLOUD: 1.1
   - TECH_PRODUCTS: 1.0
   - OTHER: 0.8

3. **Tags/Metadata** (Max: 2.0 points)
   - More tags = better metadata
   - Formula: `min(len(tags) / 5, 2)`

4. **Recency** (Bonus: 0.8 - 1.5)
   - < 24 hours: 1.5 bonus
   - < 3 days: 1.2 bonus
   - < 7 days: 1.0 bonus
   - > 7 days: 0.8 bonus

#### Priority Levels

Based on total score:

| Score Range | Priority | Description |
|------------|----------|-------------|
| ≥ 7.0 | CRITICAL | Breaking news, major announcements |
| ≥ 5.0 | HIGH | Important developments |
| ≥ 3.0 | MEDIUM | Regular news |
| < 3.0 | LOW | Minor updates, filler content |

### 3. Aggregation Dimensions

Articles are aggregated along multiple dimensions:

#### By Category
- Groups articles by the 5 main categories
- Enables category breakdown in reports
- Supports filtering by topic area

#### By Language
- Separates Korean vs. English articles
- Provides bilingual report statistics
- Supports language-specific summaries

#### By Source
- Groups articles by news site/source
- Identifies most active sources
- Enables source contribution analysis

### 4. Category Statistics

For each category, the system calculates:

- **Count**: Number of articles
- **Percentage**: % of total articles
- **Top Sources**: Most active sources for this category (top 5)
- **Top Keywords**: Most frequent keywords in titles (top 10)
- **Avg Article Length**: Average content length

### 5. Trending Keywords

Extracts top 20 trending keywords from:
- Article titles (primary source)
- Article tags (secondary source)

Filters:
- Words > 3 characters
- Excludes common stop words
- Case-insensitive matching

### 6. Report Summary

Generates a comprehensive summary including:

```python
{
    "period": {
        "start": "2026-03-17",
        "end": "2026-03-24",
        "days": 7
    },
    "total_articles": 150,
    "language_breakdown": {
        "korean": 65,
        "english": 85,
        "korean_percentage": 43.3
    },
    "category_breakdown": {
        "AI_ML": 45,
        "BLOCKCHAIN_WEB3": 25,
        "STARTUP_BUSINESS": 30,
        "TECH_PRODUCTS": 30,
        "DEVOPS_CLOUD": 20
    },
    "top_sources": [
        ("TechCrunch", 20),
        ("Bloter", 15),
        ...
    ],
    "trending_keywords": [
        ("ai", 35),
        ("startup", 28),
        ...
    ],
    "sections": {
        "TOP_STORIES": 10,
        "TRENDING_TOPICS": 15,
        "MOST_DISCUSSED": 10,
        "EDITORS_PICKS": 8,
        "NEW_THIS_WEEK": 12,
        "WEEKLY_DIGEST": 10
    }
}
```

## Usage Examples

### Basic Report Generation

```python
from datetime import datetime, timedelta
from ouroboros.crawler import (
    categorize_for_report,
    get_report_summary
)

# Assume you have crawled articles
articles = await crawler.crawl_all_sources()

# Define report period (past week)
period_start = datetime.now() - timedelta(days=7)
period_end = datetime.now()

# Categorize and aggregate articles
aggregation = categorize_for_report(
    articles=articles,
    period_start=period_start,
    period_end=period_end
)

# Access categorized data
print(f"Total articles: {aggregation.total_articles}")
print(f"AI/ML articles: {len(aggregation.by_category[Category.AI_ML])}")
print(f"Trending keywords: {aggregation.trending_keywords[:5]}")

# Get report sections
top_stories = aggregation.sections[ReportSection.TOP_STORIES]
editors_picks = aggregation.sections[ReportSection.EDITORS_PICKS]

# Generate summary
summary = get_report_summary(aggregation)
print(f"Summary: {summary}")
```

### Article Scoring

```python
from ouroboros.crawler import score_article_for_report, ReportPriority

# Score an individual article
article_score = score_article_for_report(article)

print(f"Score: {article_score.score}")
print(f"Priority: {article_score.priority}")
print(f"Reasoning: {article_score.reasoning}")

# Filter by priority
if article_score.priority == ReportPriority.CRITICAL:
    # Include in top stories
    pass
```

### Custom Report Section Creation

```python
# Create custom section from aggregated data
from ouroboros.crawler import ReportAggregation

def get_ai_ml_highlights(aggregation: ReportAggregation, limit: int = 5):
    """Get top AI/ML articles for special section."""
    ai_articles = aggregation.by_category[Category.AI_ML]

    # Sort by score
    scored = [
        (a, score_article_for_report(a).score)
        for a in ai_articles
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [a for a, score in scored[:limit]]

ai_highlights = get_ai_ml_highlights(aggregation)
```

### Category Statistics Analysis

```python
# Analyze category statistics
for category, stats in aggregation.category_stats.items():
    print(f"\n{category.value}:")
    print(f"  Count: {stats.count} ({stats.percentage}%)")
    print(f"  Avg Length: {stats.avg_article_length} chars")
    print(f"  Top Sources:")
    for source, count in stats.top_sources:
        print(f"    - {source}: {count} articles")
```

## Integration with Discord Reports

The report categorization system provides the foundation for generating Discord weekly reports:

```python
def format_discord_report(aggregation: ReportAggregation) -> str:
    """Format aggregation as Discord message."""

    summary = get_report_summary(aggregation)

    report = [
        f"# Tech News Weekly Report",
        f"**Period:** {summary['period']['start']} to {summary['period']['end']}",
        f"**Total Articles:** {summary['total_articles']}",
        "",
        "## 📊 Summary",
        f"- **Korean:** {summary['language_breakdown']['korean']} "
          f"({summary['language_breakdown']['korean_percentage']}%)",
        f"- **English:** {summary['language_breakdown']['english']}",
        "",
        "## 🔥 Top Stories",
    ]

    for article in aggregation.sections[ReportSection.TOP_STORIES][:5]:
        report.append(
            f"- **{article.title}** ({article.source})\n"
            f"  {article.url}"
        )

    report.append("")
    report.append("## 📈 Trending Topics")
    for keyword, count in summary['trending_keywords'][:5]:
        report.append(f"- {keyword} ({count} mentions)")

    return "\n".join(report)
```

## Data Models

### ReportSection (Enum)

```python
class ReportSection(str, Enum):
    TOP_STORIES = "TOP_STORIES"
    TRENDING_TOPICS = "TRENDING_TOPICS"
    CATEGORY_BREAKDOWN = "CATEGORY_BREAKDOWN"
    MOST_DISCUSSED = "MOST_DISCUSSED"
    EDITORS_PICKS = "EDITORS_PICKS"
    NEW_THIS_WEEK = "NEW_THIS_WEEK"
    WEEKLY_DIGEST = "WEEKLY_DIGEST"
```

### ReportPriority (Enum)

```python
class ReportPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
```

### CategoryStats (Dataclass)

```python
@dataclass
class CategoryStats:
    category: Category
    count: int
    percentage: float
    top_sources: list[tuple[str, int]]
    top_keywords: list[tuple[str, int]]
    avg_article_length: float
```

### ReportAggregation (Dataclass)

```python
@dataclass
class ReportAggregation:
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
```

### ArticleScore (Dataclass)

```python
@dataclass
class ArticleScore:
    article: Article
    priority: ReportPriority
    score: float
    reasoning: list[str]
```

## Public API

### Functions

#### `categorize_for_report(articles, period_start, period_end) -> ReportAggregation`

Main function to categorize and aggregate articles for report generation.

**Parameters:**
- `articles`: List[Article] - Articles to categorize
- `period_start`: datetime - Start of report period
- `period_end`: datetime - End of report period

**Returns:**
- `ReportAggregation` object with categorized data

#### `score_article_for_report(article) -> ArticleScore`

Score an article for prioritization in reports.

**Parameters:**
- `article`: Article - Article to score

**Returns:**
- `ArticleScore` object with priority, score, and reasoning

#### `get_report_summary(aggregation) -> dict`

Generate a summary of the report aggregation.

**Parameters:**
- `aggregation`: ReportAggregation - Aggregated report data

**Returns:**
- Dictionary with summary statistics

## Testing

Comprehensive test suite with 29 tests:

```bash
pytest tests/unit/crawler/test_report_categorization.py -v
```

Test coverage:
- Basic categorization
- Grouping by category, language, source
- Category statistics calculation
- Trending keyword extraction
- Report section generation
- Article scoring and prioritization
- Summary generation

All tests pass: ✅ 29/29

## Comparison: Article Classification vs. Report Categorization

| Aspect | Article Classification | Report Categorization |
|--------|---------------------|---------------------|
| **Purpose** | Categorize individual articles by topic | Organize articles for report presentation |
| **Categories** | 5 technical categories (AI_ML, etc.) | 7 report sections (TOP_STORIES, etc.) |
| **Input** | Single article (URL, title, content) | Collection of articles + time period |
| **Output** | Category enum | ReportAggregation with sections |
| **Use Case** | During crawling/post-processing | For generating weekly Discord reports |
| **Granularity** | Per-article | Aggregated/summarized |
| **Method** | Keyword matching | Scoring + ranking + aggregation |

## Best Practices

1. **Define Clear Time Periods**
   ```python
   # Good: Clear 7-day window
   period_start = datetime.now() - timedelta(days=7)
   period_end = datetime.now()

   # Avoid: Arbitrary or overlapping periods
   ```

2. **Handle Edge Cases**
   ```python
   # Check for empty results
   if aggregation.total_articles == 0:
       logger.warning("No articles in period")
       return

   # Validate sections exist before accessing
   if ReportSection.TOP_STORIES in aggregation.sections:
       top_stories = aggregation.sections[ReportSection.TOP_STORIES]
   ```

3. **Use Priorities Wisely**
   ```python
   # For alerts/notifications
   critical_articles = [
       a for a in articles
       if score_article_for_report(a).priority == ReportPriority.CRITICAL
   ]

   # For comprehensive reports
   all_prioritized = [
       (a, score_article_for_report(a))
       for a in articles
   ]
   all_prioritized.sort(key=lambda x: x[1].score, reverse=True)
   ```

4. **Combine Multiple Dimensions**
   ```python
   # Get AI articles from Korean sources
   ai_articles = aggregation.by_category[Category.AI_ML]
   korean_articles = aggregation.by_language[SourceLanguage.KOREAN]

   korean_ai = set(ai_articles) & set(korean_articles)
   ```

## Performance Considerations

- **Time Complexity**: O(n) for categorization, where n = number of articles
- **Space Complexity**: O(n) for storing categorized groups
- **Optimization**: Category statistics and trending keywords use Counter for O(1) lookups

## Future Enhancements

Potential improvements for the report categorization system:

1. **Machine Learning Scoring**
   - Use ML models for article relevance scoring
   - Incorporate user feedback on article importance

2. **Personalized Sections**
   - User-specific trending topics
   - Custom category weights

3. **Historical Analysis**
   - Week-over-week comparison
   - Trend detection over time

4. **Multilingual Keyword Extraction**
   - Better Korean keyword handling
   - Cross-language topic clustering

5. **Source Quality Scoring**
   - Track source reliability
   - Weight articles by source credibility

## Related Documentation

- [README.md](README.md) - Main crawler documentation
- [classification.py](classification.py) - Article classification (5 categories)
- [models.py](models.py) - Article and category data models
- [ENHANCED_ERROR_HANDLING.md](ENHANCED_ERROR_HANDLING.md) - Error handling guide

## License

Part of the Ouroboros AI Workflow System project.
