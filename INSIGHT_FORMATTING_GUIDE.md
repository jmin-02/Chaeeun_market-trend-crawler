# Insight Formatting for Discord Reports

This guide explains how to format and present extracted insights from tech news articles in Discord weekly reports.

## Overview

The insight formatting system transforms structured data extracted from articles into visually appealing, Discord-compatible messages. It supports:

- **Skills**: Programming languages, frameworks, tools with relevance scores
- **Companies**: Tech companies with action types and metrics
- **Salaries**: Salary ranges with currency and period
- **Job Titles**: Positions with experience levels and counts
- **Locations**: Geographic locations and remote work indicators
- **Key Takeaways**: AI-scored important points from articles

## Discord Emojis

### Insight Category Emojis

| Category | Emoji | Description |
|-----------|-------|-------------|
| HIRING_TRENDS | 📊 | Hiring trends and market movements |
| IN_DEMAND_SKILLS | 💡 | Most requested skills |
| COMPANY_NEWS | 🏢 | Company updates and news |
| SALARY_BENEFITS | 💰 | Salary and compensation info |
| CAREER_DEVELOPMENT | 📈 | Growth and learning opportunities |
| JOB_OPENINGS | 🎯 | Specific job postings |
| INDUSTRY_OUTLOOK | 🔮 | Market predictions and trends |
| TECH_UPDATES | ⚙️ | New technology releases |
| WORKPLACE_CULTURE | 🏠 | Company culture and policies |
| EDUCATION_TRAINING | 📚 | Learning resources and courses |
| OTHER | 📄 | General news |

### Skill Level Emojis

| Level | Emoji | Description |
|-------|--------|-------------|
| JUNIOR | 🌱 | Entry-level positions |
| MID | 🌿 | Mid-level experience |
| SENIOR | 🌳 | Senior roles |
| LEAD | 🏆 | Team leads |
| PRINCIPAL | 👑 | Principal engineers |
| EXECUTIVE | 🎖️ | C-level positions |

### Company Action Emojis

| Action | Emoji | Description |
|--------|--------|-------------|
| hiring | 👥 | Recruiting new staff |
| funding | 💵 | Investment rounds |
| acquisition | 🤝 | M&A activity |
| expansion | 📍 | Office/region expansion |
| ipo | 📈 | Public offerings |
| layoff | 📉 | Staff reductions |
| launch | 🚀 | Product launches |

### Location Type Emojis

| Type | Emoji | Description |
|------|--------|-------------|
| city | 🏙️ | Urban locations |
| country | 🌍 | National locations |
| remote | 🏡 | Work-from-home |

## Formatting Functions

### 1. Individual Insight Formatting

#### Skills

```python
from ouroboros.crawler import format_skill, ExtractedSkill

skill = ExtractedSkill(
    skill="Python",
    category="programming",
    level=SkillLevel.SENIOR,
    relevance_score=0.9,
    context="Python is essential for this role"
)

# Format without context
formatted = format_skill(skill, show_context=False)
print(formatted)
```

**Output:**
```
🔥 `Python` - **programming** 🌳
   Relevance: 0.90
```

#### Companies

```python
from ouroboros.crawler import format_company, ExtractedCompany

company = ExtractedCompany(
    name="Google",
    context="Google is hiring 100 engineers",
    action="hiring",
    metrics={"hiring_count": 100}
)

formatted = format_company(company, show_context=True)
```

**Output:**
```
👥 **Google** - *hiring*
   📊 hiring_count: 100
   Context: *Google is hiring 100 engineers*
```

#### Salaries

```python
from ouroboros.crawler import format_salary, ExtractedSalary

salary = ExtractedSalary(
    amount_min=100000,
    amount_max=150000,
    currency="USD",
    period="annual",
    role="Senior Engineer"
)

formatted = format_salary(salary, show_context=False)
```

**Output:**
```
💰 **USD 100000 - 150000**
   Period: *annual*
   Role: `Senior Engineer`
```

#### Job Titles

```python
from ouroboros.crawler import format_job_title, ExtractedJobTitle

job_title = ExtractedJobTitle(
    title="Senior Software Engineer",
    level=SkillLevel.SENIOR,
    company="Tech Corp",
    location="San Francisco",
    count=5
)

formatted = format_job_title(job_title, show_context=False)
```

**Output:**
```
🎯 **Senior Software Engineer**
   Level: *SkillLevel.SENIOR*
   Company: `Tech Corp`
   Location: `San Francisco`
   Positions: **5**
```

#### Locations

```python
from ouroboros.crawler import format_location, ExtractedLocation

location = ExtractedLocation(
    location="Remote",
    context="Remote work available",
    type="remote"
)

formatted = format_location(location, show_context=True)
```

**Output:**
```
🏡 **Remote**
   Type: *remote*
   Context: *Remote work available*
```

### 2. Section Formatting

#### Skills Section

```python
from ouroboros.crawler import format_skills_section, SourceLanguage

skills = [
    ExtractedSkill(skill="Python", category="programming", level=SkillLevel.SENIOR, relevance_score=0.9),
    ExtractedSkill(skill="JavaScript", category="programming", level=SkillLevel.MID, relevance_score=0.8),
]

section = format_skills_section(
    skills,
    title="Top Skills This Week",
    language=SourceLanguage.ENGLISH,
    max_skills=10
)
```

**Output:**
```
💡 **Top Skills This Week**
==================================================

1. 🔥 `Python` - **programming** 🌳
   Relevance: 0.90

2. ⭐ `JavaScript` - **programming** 🌿
   Relevance: 0.80
```

#### Companies Section

```python
from ouroboros.crawler import format_companies_section

companies = [
    ExtractedCompany(name="Google", context="Google hiring", action="hiring"),
    ExtractedCompany(name="Microsoft", context="Microsoft funding", action="funding"),
]

section = format_companies_section(
    companies,
    title="Company Updates",
    language=SourceLanguage.ENGLISH,
    max_companies=8
)
```

**Output:**
```
🏢 **Company Updates**
==================================================

1. 👥 **Google** - *hiring*

2. 💵 **Microsoft** - *funding*
```

#### Salaries Section

```python
from ouroboros.crawler import format_salaries_section

salaries = [
    ExtractedSalary(
        amount_min=100000, amount_max=150000,
        currency="USD", period="annual",
        role="Senior Engineer"
    ),
]

section = format_salaries_section(
    salaries,
    title="Salary Ranges",
    language=SourceLanguage.ENGLISH,
    max_salaries=6
)
```

**Output:**
```
💰 **Salary Ranges**
==================================================

1. 💰 **USD 100000 - 150000**
   Period: *annual*
   Role: `Senior Engineer`
```

### 3. Comprehensive Reports

#### Single Article Insight Report

```python
from ouroboros.crawler import format_insight_report, ExtractedInsight

insight = ExtractedInsight(
    insight_category=InsightCategory.IN_DEMAND_SKILLS,
    skills=[
        ExtractedSkill(skill="Python", category="programming", level=SkillLevel.SENIOR, relevance_score=0.9),
    ],
    companies=[
        ExtractedCompany(name="Google", context="Google hiring", action="hiring"),
    ],
)

report = format_insight_report(
    insight,
    article_title="Top Tech Skills for 2024",
    language=SourceLanguage.ENGLISH
)
```

#### Weekly Insights Report

```python
from ouroboros.crawler import format_weekly_insights_report, Article

# Create article-insight pairs
articles_insights = [
    (article1, insight1),
    (article2, insight2),
    # ... more pairs
]

report = format_weekly_insights_report(
    articles_insights,
    language=SourceLanguage.ENGLISH,
    max_articles=5
)
```

**Output includes:**
- Summary statistics (total skills, companies, salaries, etc.)
- Top skills section
- Top companies section
- Salary highlights
- Job opportunities section
- Top articles with their insights

## Bilingual Support

All formatting functions support Korean and English:

```python
# English report
section = format_skills_section(skills, language=SourceLanguage.ENGLISH)

# Korean report
section = format_skills_section(skills, language=SourceLanguage.KOREAN)
```

## Best Practices

### 1. Relevance Indicators

Skills use visual indicators based on relevance score:
- 🔥 High relevance (≥0.7)
- ⭐ Medium relevance (≥0.5)
- 📌 Low relevance (<0.5)

### 2. Context Snippets

Use `show_context=True` to include article context:
- Helps users understand why an insight was extracted
- Limited to 100 characters for readability
- Escaped for Discord safety

### 3. Result Limiting

Sections support limiting results:
- Prevents message length issues
- Focuses on top insights
- Default limits: 10 skills, 8 companies, 6 salaries, etc.

### 4. Sorting

Insights are automatically sorted:
- **Skills**: By relevance score (descending)
- **Companies**: By action priority (hiring > funding > acquisition)
- **Salaries**: By maximum salary (descending)
- **Locations**: Remote first, then cities, then countries
- **Job Titles**: By position count (descending)

### 5. Empty Data Handling

All sections handle empty data gracefully:
- Display "*No [type] extracted*" message
- Avoids errors with missing data
- Clear user feedback

## Integration Example

### Complete Workflow

```python
from ouroboros.crawler import (
    Article,
    classify_insight,
    extract_insights,
    format_weekly_insights_report,
    InsightCategory,
    SourceLanguage,
)

# Step 1: Classify article
category = classify_insight(
    url="https://example.com/article",
    title="Top Skills for 2024",
    content="Python and JavaScript are most in-demand..."
)

# Step 2: Extract insights
insights = extract_insights(
    title="Top Skills for 2024",
    content="Python and JavaScript are most in-demand...",
    insight_category=category,
    language=SourceLanguage.ENGLISH,
)

# Step 3: Format for Discord
article = Article(
    title="Top Skills for 2024",
    url="https://example.com/article",
    content="Python and JavaScript are most in-demand...",
    source="Tech Blog",
    published_at=datetime.now(),
    language=SourceLanguage.ENGLISH,
)

report = format_weekly_insights_report(
    [(article, insights)],
    language=SourceLanguage.ENGLISH,
    max_articles=5
)

# Step 4: Send to Discord (pseudo-code)
discord_client.send_message(channel_id, report)
```

## Discord Message Structure

### Discord Markdown Safety

All text is properly escaped:
- Asterisks (*): `\*`
- Underscores (_): `\_`
- Tildes (~): `\~`
- Pipes (|): `\|`
- Backticks (`): `\``

### Visual Hierarchy

```
# Main Title
==================================================

## Section Title
--------------------------------------------------

1. **Item Title**
   Subtitle
   Detail

```

### Emojis as Visual Cues

- Section headers: Category/section emoji
- High priority: 🔥 (fire)
- Medium priority: ⭐ (star)
- Low priority: 📌 (pin)
- Fresh content: 🆕 (new)

## Performance Considerations

### Time Complexity

- Individual formatting: O(1) - simple string formatting
- Section formatting: O(n log n) - sorting n items
- Weekly report: O(n) - processing n articles

### Space Complexity

- O(n) - storing formatted output
- O(k) - where k is result limit

### Optimization Tips

1. **Limit Results**: Use `max_*` parameters to control output size
2. **Pre-sort**: Sort insights before formatting to avoid duplicate sorting
3. **Cache Context**: Avoid recalculating context snippets
4. **Batch Operations**: Format multiple items at once when possible

## Troubleshooting

### Issue: Messages too long for Discord

**Solution**: Reduce `max_*` limits or split into multiple messages

```python
# Smaller sections
section = format_skills_section(skills, max_skills=5)

# Or split into multiple messages
for i in range(0, len(skills), 5):
    section = format_skills_section(skills[i:i+5], max_skills=5)
    discord.send(channel, section)
```

### Issue: Missing emojis

**Solution**: Verify emoji names in `DiscordEmoji` enum

```python
from ouroboros.crawler import DiscordEmoji

# List all available emojis
for emoji in DiscordEmoji:
    print(f"{emoji.name}: {emoji.value}")
```

### Issue: Incorrect field names

**Solution**: Check data class signatures

```python
from ouroboros.crawler.insight_extraction import ExtractedCompany

# Check required fields
print(ExtractedCompany.__annotations__)
```

### Issue: Text not displaying correctly

**Solution**: Ensure proper escaping

```python
from ouroboros.crawler import escape_discord

text = "Special *characters* here"
escaped = escape_discord(text)
# Output: "Special \\*characters\\* here"
```

## Testing

### Running Tests

```bash
# Run all Discord formatter tests
pytest tests/unit/crawler/test_discord_formatter.py -v

# Run only insight formatting tests
pytest tests/unit/crawler/test_discord_formatter.py::TestFormatSkill -v
pytest tests/unit/crawler/test_discord_formatter.py::TestFormatCompany -v
pytest tests/unit/crawler/test_discord_formatter.py::TestFormatSalary -v
```

### Test Coverage

- 95 tests total
- 37 original article/category tests
- 58 new insight formatting tests
- All tests passing ✅

### Test Categories

1. **Emoji Tests**: Category, section, status emojis
2. **Individual Insight Tests**: Skills, companies, salaries, job titles, locations
3. **Section Tests**: Multi-item formatting with limits
4. **Comprehensive Report Tests**: Single article and weekly reports
5. **Bilingual Tests**: Korean and English support
6. **Edge Case Tests**: Empty data, special characters, Unicode

## API Reference

### Formatting Functions

```python
def get_insight_emoji(insight_category: InsightCategory) -> DiscordEmoji:
    """Get Discord emoji for an insight category."""

def format_skill(skill: ExtractedSkill, show_context: bool = False) -> str:
    """Format a single extracted skill for Discord."""

def format_skills_section(
    skills: list[ExtractedSkill],
    title: str = "In-Demand Skills",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_skills: int = 10
) -> str:
    """Format a section displaying extracted skills."""

def format_company(company: ExtractedCompany, show_context: bool = False) -> str:
    """Format a single extracted company for Discord."""

def format_companies_section(
    companies: list[ExtractedCompany],
    title: str = "Company News",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_companies: int = 8
) -> str:
    """Format a section displaying extracted companies."""

def format_salary(salary: ExtractedSalary, show_context: bool = False) -> str:
    """Format a single extracted salary for Discord."""

def format_salaries_section(
    salaries: list[ExtractedSalary],
    title: str = "Salary Information",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_salaries: int = 6
) -> str:
    """Format a section displaying extracted salaries."""

def format_job_title(job_title: ExtractedJobTitle, show_context: bool = False) -> str:
    """Format a single extracted job title for Discord."""

def format_job_titles_section(
    job_titles: list[ExtractedJobTitle],
    title: str = "Job Openings",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_titles: int = 8
) -> str:
    """Format a section displaying extracted job titles."""

def format_location(location: ExtractedLocation, show_context: bool = False) -> str:
    """Format a single extracted location for Discord."""

def format_locations_section(
    locations: list[ExtractedLocation],
    title: str = "Job Locations",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_locations: int = 6
) -> str:
    """Format a section displaying extracted locations."""

def format_key_takeaways_section(
    takeaways: list[tuple[str, float]],
    title: str = "Key Takeaways",
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_takeaways: int = 5
) -> str:
    """Format a section displaying key takeaways."""

def format_insight_report(
    insight: ExtractedInsight,
    article_title: str = "Article",
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> str:
    """Format a comprehensive insight report for a single article."""

def format_weekly_insights_report(
    articles_insights: list[tuple[Article, ExtractedInsight]],
    language: SourceLanguage = SourceLanguage.ENGLISH,
    max_articles: int = 5
) -> str:
    """Format a weekly insights report from multiple articles."""
```

## Future Enhancements

1. **Rich Embeds**: Use Discord embed objects for richer formatting
2. **Interactive Components**: Add buttons for filtering/sorting
3. **Thumbnails**: Include article/company logos
4. **Links**: Add clickable links to sources
5. **Highlighting**: Highlight key terms in context snippets
6. **Pagination**: Split long reports into pages
7. **Notifications**: Add mention for high-priority insights
8. **Analytics**: Track which insights users click on

## Conclusion

The insight formatting system provides:

- **Visual Appeal**: Emojis and structured formatting
- **Readability**: Clear hierarchy and organization
- **Bilingual Support**: Korean and English
- **Discord Compatibility**: Proper markdown escaping
- **Comprehensive Coverage**: All insight types
- **Production Ready**: Fully tested and documented

For questions or issues, refer to the main crawler documentation or create an issue.
