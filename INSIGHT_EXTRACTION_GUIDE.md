# Insight Extraction Guide

## Overview

The insight extraction module goes beyond simple categorization to extract specific, structured insights from articles that are valuable for job seekers. This complements the insight categorization module by providing detailed extraction of entities, metrics, and actionable information.

## Features

### What Gets Extracted

#### 1. Skills (`ExtractedSkill`)
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks (React, Vue, Django, etc.)
- Cloud services (AWS, Azure, GCP, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- DevOps tools (Docker, Kubernetes, Jenkins, etc.)

Each skill includes:
- `skill`: Name of the skill
- `category`: Type of skill (programming_language, framework, cloud_service, database, devops_tool)
- `level`: Experience level (junior, mid, senior, lead, principal, executive)
- `context`: Surrounding text showing how the skill was mentioned
- `relevance_score`: 0.0-1.0 score based on context importance

#### 2. Companies (`ExtractedCompany`)
- Company names (Google, Microsoft, Naver, Kakao, etc.)
- Action type: hiring, funding, expanding, layoffs, acquisition, IPO
- Quantitative metrics: hiring counts, funding amounts, growth percentages

Each company includes:
- `name`: Company name
- `context`: Surrounding text
- `action`: What the company is doing
- `metrics`: Dictionary of quantitative data

#### 3. Salaries (`ExtractedSalary`)
- Salary ranges and amounts
- Currency and period (annual, monthly, hourly)
- Role and company context
- Location information

#### 4. Job Titles (`ExtractedJobTitle`)
- Specific job titles and roles
- Experience level indicators
- Company and location
- Position count if mentioned

#### 5. Locations (`ExtractedLocation`)
- Geographic locations
- Location type: city, country, region, remote
- Contextual information

#### 6. Key Takeaways
- AI-extracted key points for job seekers
- Scored by relevance
- Limited to top 3 per article

#### 7. Quantitative Data
- Percentages (growth rates, increases)
- Large numbers (funding amounts, hiring counts)
- Growth metrics

## Usage

### Basic Extraction

```python
from ouroboros.crawler import (
    extract_insights,
    InsightCategory,
    SourceLanguage,
)

# Extract insights from an article
title = "Most In-Demand Tech Skills for 2024"
content = """
Python and JavaScript are the most sought-after skills.
Companies require cloud computing experience.
DevOps tools like Docker and Kubernetes are essential.
"""

insights = extract_insights(
    title=title,
    content=content,
    insight_category=InsightCategory.IN_DEMAND_SKILLS,
    language=SourceLanguage.ENGLISH,
)

# Access extracted data
print(f"Skills found: {len(insights.skills)}")
for skill in insights.skills:
    print(f"  - {skill.skill} (relevance: {skill.relevance_score:.2f})")

# Convert to dictionary for storage/serialization
insights_dict = insights.to_dict()
```

### Extracting Specific Types

```python
from ouroboros.crawler import (
    extract_skills,
    extract_companies,
    extract_salaries,
    extract_job_titles,
    extract_locations,
    SourceLanguage,
)

# Extract only skills
skills = extract_skills(article_text, SourceLanguage.ENGLISH)

# Extract only companies
companies = extract_companies(article_text, SourceLanguage.ENGLISH)

# Extract only salaries
salaries = extract_salaries(article_text, SourceLanguage.ENGLISH)

# Extract only job titles
job_titles = extract_job_titles(article_text, SourceLanguage.ENGLISH)

# Extract only locations
locations = extract_locations(article_text, SourceLanguage.ENGLISH)
```

### Category-Specific Extraction

The `extract_insights` function automatically determines what to extract based on the insight category:

- **IN_DEMAND_SKILLS**: Extracts skills
- **COMPANY_NEWS**: Extracts companies and metrics
- **SALARY_BENEFITS**: Extracts salaries
- **JOB_OPENINGS**: Extracts job titles, skills, salaries, and locations
- **HIRING_TRENDS**: Extracts companies and quantitative data

### Korean Content Support

```python
from ouroboros.crawler import extract_insights, InsightCategory, SourceLanguage

korean_article = """
2024년 인기 기술 스킬
Python과 JavaScript가 가장 인기 있는 스킬입니다.
기업들은 클라우드 경험을 요구합니다.
"""

insights = extract_insights(
    title="2024년 인기 기술 스킬",
    content=korean_article,
    insight_category=InsightCategory.IN_DEMAND_SKILLS,
    language=SourceLanguage.KOREAN,
)
```

Note: Technical skills are matched against English keywords regardless of text language, so "Python", "JavaScript", etc. will be found in Korean text.

## Data Models

### ExtractedSkill

```python
@dataclass
class ExtractedSkill:
    skill: str
    category: str  # programming_language, framework, cloud_service, database, devops_tool
    level: SkillLevel  # junior, mid, senior, lead, principal, executive
    context: str
    relevance_score: float  # 0.0-1.0
```

### ExtractedCompany

```python
@dataclass
class ExtractedCompany:
    name: str
    context: str
    action: str  # hiring, funding, expanding, layoffs, acquisition, ipo
    metrics: dict[str, Union[int, float, str]]
```

### ExtractedSalary

```python
@dataclass
class ExtractedSalary:
    amount_min: Optional[Union[int, float]]
    amount_max: Optional[Union[int, float]]
    currency: str  # USD, KRW, etc.
    period: str  # annual, monthly, hourly
    role: str
    company: str
    location: str
    context: str
```

### ExtractedJobTitle

```python
@dataclass
class ExtractedJobTitle:
    title: str
    level: SkillLevel
    company: str
    location: str
    count: Optional[int]  # Number of positions
    context: str
```

### ExtractedLocation

```python
@dataclass
class ExtractedLocation:
    location: str
    type: str  # city, country, region, remote
    context: str
```

### ExtractedInsight

```python
@dataclass
class ExtractedInsight:
    insight_category: InsightCategory
    skills: list[ExtractedSkill]
    companies: list[ExtractedCompany]
    salaries: list[ExtractedSalary]
    job_titles: list[ExtractedJobTitle]
    locations: list[ExtractedLocation]
    key_takeaways: list[str]
    quantitative_data: dict[str, Any]
```

## Technical Details

### Skill Extraction Algorithm

1. **Keyword Matching**: Searches for predefined skill keywords in text
2. **Context Validation**: Ensures skills are not part of longer words
3. **Categorization**: Assigns skill to category (programming language, framework, etc.)
4. **Context Extraction**: Extracts surrounding text for each skill
5. **Relevance Scoring**: Scores each skill based on context indicators
6. **Deduplication**: Removes duplicate skills, keeping highest relevance
7. **Ranking**: Sorts by relevance and limits to top 20

### Company Extraction

- Uses a hardcoded list of tech companies
- Detects company actions (hiring, funding, expansion, etc.)
- Extracts quantitative metrics from context

### Salary Extraction

- Supports multiple formats:
  - `$150,000 - $180,000`
  - `$130k`
  - `5천만원` (Korean)
  - `연봉 5000`

### Job Title Extraction

- Matches patterns like:
  - "Senior Software Engineer"
  - "Junior Python Developer"
  - "시니어 소프트웨어 엔지니어" (Korean)
- Detects experience level from title
- Extracts position count if mentioned

### Location Extraction

- Matches city names, countries, and remote work indicators
- Detects location type (city, country, remote)
- Supports both English and Korean locations

## Limitations and Future Improvements

### Current Limitations

1. **Hardcoded Lists**: Companies, skills, and locations use hardcoded lists
2. **Pattern-Based**: Relies on regex patterns which may miss variations
3. **No NER**: Doesn't use Named Entity Recognition for better entity extraction
4. **Context Simple**: Relevance scoring is heuristic-based

### Future Improvements

1. **NER Integration**: Use spaCy or similar for better entity extraction
2. **ML Models**: Train models for better relevance scoring
3. **Dynamic Lists**: Update skill and company lists from crawled content
4. **Advanced Context**: Better semantic understanding of context
5. **Relationship Extraction**: Extract relationships between entities

## Best Practices

### 1. Combine with Classification

```python
from ouroboros.crawler import (
    classify_insight,
    extract_insights,
    SourceLanguage,
)

# First classify the article
category = classify_insight(url, title, content)

# Then extract insights based on category
insights = extract_insights(
    title=title,
    content=content,
    insight_category=category,
    language=SourceLanguage.ENGLISH,
)
```

### 2. Validate Extracted Data

```python
# Always check if extraction returned data
if insights.skills:
    for skill in insights.skills:
        if skill.relevance_score > 0.7:
            print(f"High relevance skill: {skill.skill}")

if insights.salaries:
    for salary in insights.salaries:
        if salary.amount_min and salary.amount_min > 100000:
            print(f"High-paying role: {salary.role}")
```

### 3. Handle Bilingual Content

```python
# Detect language or use metadata
language = detect_language(article_text) or SourceLanguage.ENGLISH

# Extract with correct language parameter
insights = extract_insights(
    title=title,
    content=content,
    insight_category=category,
    language=language,
)
```

### 4. Store Extracted Data

```python
import json

# Convert to dict and serialize
insights_dict = insights.to_dict()
json_data = json.dumps(insights_dict, indent=2)

# Store in database or file
# db.insert('insights', json_data)
# or
# with open('insights.json', 'w') as f:
#     f.write(json_data)
```

## Testing

Run the test suite:

```bash
pytest tests/unit/crawler/test_insight_extraction.py -v
```

Test coverage includes:
- Skill extraction (English and Korean)
- Company extraction with actions and metrics
- Salary extraction (multiple formats)
- Job title extraction
- Location extraction
- Key takeaway extraction
- Quantitative data extraction
- Edge cases and error handling

## Integration with Crawler Framework

### Example: Enhanced Article Processing

```python
from ouroboros.crawler import (
    BaseCrawler,
    Article,
    classify_insight,
    extract_insights,
    SourceLanguage,
)

class EnhancedCrawler(BaseCrawler):
    def extract_articles(self, html: str, source: str, language: str = "en") -> list[Article]:
        # Extract articles using base implementation
        articles = super().extract_articles(html, source, language)

        # Enhance each article with insights
        for article in articles:
            # Classify insight category
            article.insight_category = classify_insight(
                str(article.url),
                article.title,
                article.content
            )

            # Extract insights
            lang = SourceLanguage.KOREAN if language == "ko" else SourceLanguage.ENGLISH
            insights = extract_insights(
                article.title,
                article.content,
                article.insight_category,
                lang
            )

            # Store insights (e.g., as JSON in summary field)
            article.summary = json.dumps(insights.to_dict())

        return articles
```

## Performance Considerations

### Extraction Limits

To prevent performance issues and excessive memory usage:
- Skills: Limited to top 20
- Companies: Limited to top 10
- Salaries: Limited to top 5
- Job Titles: Limited to top 10
- Locations: Limited to top 5
- Key Takeaways: Limited to top 3

### Optimization Tips

1. **Batch Processing**: Extract insights for multiple articles in batches
2. **Caching**: Cache skill/company lists for reuse
3. **Lazy Extraction**: Only extract when needed (e.g., before display/storage)
4. **Parallel Processing**: Use asyncio for concurrent extraction

## Troubleshooting

### Skills Not Found

**Problem**: Skills not extracted from text
**Solutions**:
- Check if skill is in the predefined lists
- Verify text contains the skill as a standalone word
- Check character encoding for non-ASCII text
- Verify case sensitivity (extraction is case-insensitive)

### Companies Not Extracted

**Problem**: Companies not found
**Solutions**:
- Check if company name is in the predefined list
- Verify company name is mentioned exactly
- Add company to the list if commonly encountered

### Salary Parsing Fails

**Problem**: Salaries not extracted
**Solutions**:
- Verify salary format matches patterns
- Check for currency symbols
- Try alternative formats in test cases

## API Reference

See the docstrings in `insight_extraction.py` for complete API documentation of each function:

- `extract_insights()`: Main extraction function
- `extract_skills()`: Skill-specific extraction
- `extract_companies()`: Company-specific extraction
- `extract_salaries()`: Salary-specific extraction
- `extract_job_titles()`: Job title extraction
- `extract_locations()`: Location extraction
- `extract_key_takeaways()`: Key takeaway extraction
- `extract_quantitative_data()`: Quantitative data extraction

## Support

For issues or questions:
1. Check test cases for usage examples
2. Review this guide for best practices
3. Examine source code for implementation details
4. Run tests to verify functionality
