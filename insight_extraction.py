"""Insight extraction module for job seeker-focused tech news analysis.

This module provides extraction of specific, structured insights from articles,
going beyond simple categorization to identify actionable information for job seekers.

Extraction includes:
- Specific skills mentioned
- Companies mentioned with context
- Salary ranges when available
- Job titles/roles mentioned
- Locations mentioned
- Quantitative metrics (hiring numbers, funding amounts, etc.)
- Key takeaways for job seekers
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from typing import Any, Optional, Union

from .insight_categorization import InsightCategory
from .models import SourceLanguage

logger = logging.getLogger(__name__)


class SkillLevel(str, Enum):
    """Skill level indicators."""

    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"
    ALL_LEVELS = "all_levels"
    UNKNOWN = "unknown"


@dataclass
class ExtractedSkill:
    """Extracted skill information."""

    skill: str
    category: str = "general"  # programming_language, framework, soft_skill, etc.
    level: SkillLevel = SkillLevel.UNKNOWN
    context: str = ""  # How the skill was mentioned
    relevance_score: float = 0.5  # 0.0-1.0, based on context

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill,
            "category": self.category,
            "level": self.level.value,
            "context": self.context,
            "relevance_score": self.relevance_score,
        }


@dataclass
class ExtractedCompany:
    """Extracted company information."""

    name: str
    context: str  # How the company was mentioned
    action: str = "mentioned"  # hiring, funding, acquisition, expanding, etc.
    metrics: dict[str, Union[int, float, str]] = field(default_factory=dict)
    # e.g., {"hiring_count": 100, "funding_amount": "50M"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "context": self.context,
            "action": self.action,
            "metrics": self.metrics,
        }


@dataclass
class ExtractedSalary:
    """Extracted salary information."""

    amount_min: Optional[Union[int, float]] = None
    amount_max: Optional[Union[int, float]] = None
    currency: str = "USD"
    period: str = "annual"  # annual, monthly, hourly
    role: str = ""
    company: str = ""
    location: str = ""
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "amount_min": self.amount_min,
            "amount_max": self.amount_max,
            "currency": self.currency,
            "period": self.period,
            "role": self.role,
            "company": self.company,
            "location": self.location,
            "context": self.context,
        }


@dataclass
class ExtractedJobTitle:
    """Extracted job title information."""

    title: str
    level: SkillLevel = SkillLevel.UNKNOWN
    company: str = ""
    location: str = ""
    count: Optional[int] = None  # Number of positions if mentioned
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "level": self.level.value,
            "company": self.company,
            "location": self.location,
            "count": self.count,
            "context": self.context,
        }


@dataclass
class ExtractedLocation:
    """Extracted location information."""

    location: str
    type: str = "city"  # city, country, region, remote
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "type": self.type,
            "context": self.context,
        }


@dataclass
class ExtractedInsight:
    """Comprehensive extracted insights from an article."""

    insight_category: InsightCategory
    skills: list[ExtractedSkill] = field(default_factory=list)
    companies: list[ExtractedCompany] = field(default_factory=list)
    salaries: list[ExtractedSalary] = field(default_factory=list)
    job_titles: list[ExtractedJobTitle] = field(default_factory=list)
    locations: list[ExtractedLocation] = field(default_factory=list)
    key_takeaways: list[str] = field(default_factory=list)
    quantitative_data: dict[str, Any] = field(default_factory=dict)
    # e.g., {"hiring_growth_rate": "15%", "market_size": "$10B"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "insight_category": self.insight_category.value if isinstance(self.insight_category, InsightCategory) else self.insight_category,
            "skills": [skill.to_dict() for skill in self.skills],
            "companies": [company.to_dict() for company in self.companies],
            "salaries": [salary.to_dict() for salary in self.salaries],
            "job_titles": [title.to_dict() for title in self.job_titles],
            "locations": [location.to_dict() for location in self.locations],
            "key_takeaways": self.key_takeaways,
            "quantitative_data": self.quantitative_data,
        }


# Common programming languages and frameworks
PROGRAMMING_LANGUAGES = {
    "python", "javascript", "java", "golang", "go", "rust", "typescript",
    "c++", "c#", "ruby", "php", "swift", "kotlin", "scala", "clojure",
    "haskell", "elm", "erlang", "dart", "lua", "perl", "r", "matlab"
}

FRAMEWORKS = {
    "react", "vue", "angular", "svelte", "django", "flask", "fastapi",
    "spring", "express", "nest", "rails", "laravel", "asp.net", "gin",
    "fiber", "echo", "fiber", "tokio", "actix", "rocket", "ember",
    "backbone", "knockout", "mithril", "riot", "polymer"
}

CLOUD_SERVICES = {
    "aws", "azure", "gcp", "google cloud", "google cloud platform",
    "kubernetes", "docker", "terraform", "ansible", "chef", "puppet",
    "serverless", "lambda", "functions", "cloud functions"
}

DATABASES = {
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "cosmosdb", "firestore", "firebase",
    "sqlite", "mariadb", "oracle", "sql server", "mssql"
}

DEVOPS_TOOLS = {
    "jenkins", "gitlab", "circleci", "travisci", "github actions",
    "bitbucket pipelines", "spinnaker", "argo", "helm", "prometheus",
    "grafana", "elk", "splunk", "datadog", "new relic"
}

ALL_TECH_KEYWORDS = PROGRAMMING_LANGUAGES | FRAMEWORKS | CLOUD_SERVICES | DATABASES | DEVOPS_TOOLS

# Common job title patterns
JOB_TITLE_PATTERNS = {
    "english": [
        r"senior\s+(\w+)\s+engineer",
        r"lead\s+(\w+)\s+engineer",
        r"principal\s+(\w+)\s+engineer",
        r"staff\s+(\w+)\s+engineer",
        r"junior\s+(\w+)\s+engineer",
        r"mid-level\s+(\w+)\s+engineer",
        r"entry-level\s+(\w+)\s+engineer",
        r"(\w+)\s+developer",
        r"(\w+)\s+engineer",
        r"(\w+)\s+architect",
        r"(\w+)\s+manager",
        r"(\w+)\s+analyst",
        r"(\w+)\s+designer",
        r"data\s+scientist",
        r"machine\s+learning\s+engineer",
        r"ai\s+engineer",
        r"devops\s+engineer",
        r"site\s+reliability\s+engineer",
        r"full\s+stack\s+developer",
        r"frontend\s+developer",
        r"backend\s+developer",
        r"mobile\s+developer",
        r"ios\s+developer",
        r"android\s+developer",
    ],
    "korean": [
        r"시니어\s*(.+?)\s*엔지니어",
        r"리드\s*(.+?)\s*엔지니어",
        r"주니어\s*(.+?)\s*엔지니어",
        r"신입\s*(.+?)\s*엔지니어",
        r"중급\s*(.+?)\s*엔지니어",
        r"(.+?)\s*개발자",
        r"(.+?)\s*엔지니어",
        r"(.+?)\s*아키텍트",
        r"(.+?)\s*매니저",
        r"(.+?)\s*분석가",
        r"(.+?)\s*디자이너",
        r"데이터\s*사이언티스트",
        r"머신러닝\s*엔지니어",
        r"ai\s*엔지니어",
        r"데브옵스\s*엔지니어",
        r"풀스택\s*개발자",
        r"프론트엔드\s*개발자",
        r"백엔드\s*개발자",
        r"모바일\s*개발자",
    ]
}

# Company action patterns
COMPANY_ACTIONS = {
    "hiring": r"(is\s+(are\s+)?hiring|recruiting|looking\s+for|we're\s+hiring|join\s+our\s+team)",
    "funding": r"(raised|secured|funding|investment|series\s+[abc]|investment\s+round)",
    "expanding": r"(expanding|opening\s+new\s+office|global\s+expansion|growing)",
    "layoffs": r"(layoff|lay\s+off|firing|cutting\s+jobs|workforce\s+reduction)",
    "acquisition": r"(acquired|bought|merger|acquisition|buyout)",
    "ipo": r"(ipo|public\s+offering|going\s+public|listed\s+on\s+)",
}

# Salary patterns
SALARY_PATTERNS = {
    "english": [
        r"\$\s*(\d+(?:,\d+)*(?:\.\d+)?)(?:\s*-\s*\$\s*(\d+(?:,\d+)*(?:\.\d+)?))?(?:\s*k)",
        r"\$(\d+(?:,\d+)*(?:\.\d+)?)(?:\s*-\s*\$(\d+(?:,\d+)*(?:\.\d+)?))?\s*-\s*\$?\d+(?:,\d+)*(?:\.\d+)?",
        r"(\d+(?:,\d+)*(?:\.\d+)?)\s*usd",
        r"(\d+(?:,\d+)*(?:\.\d+)?)\s*thousand",
        r"(\d+(?:,\d+)*(?:\.\d+)?)\s*million",
    ],
    "korean": [
        r"(\d+(?:,\d+)*(?:\.\d+)?)\s*만원",
        r"(\d+(?:,\d+)*(?:\.\d+)?)\s*천만원",
        r"(\d+(?:,\d+)*(?:\.\d+)?)\s*억원",
        r"연봉\s*(\d+(?:,\d+)*(?:\.\d+)?)",
    ]
}

# Location patterns
LOCATION_PATTERNS = {
    "english": [
        r"(?:in|at|from)\s+([A-Z][a-z\s]+(?:,\s*[A-Z][a-z\s]+)?)",
        r"(?:San Francisco|New York|Los Angeles|Seattle|Boston|Austin|Chicago|Washington DC|London|Berlin|Singapore|Tokyo|Seoul)",
        r"(remote|work\s+from\s+anywhere|distributed)",
    ],
    "korean": [
        r"(?:서울|부산|대구|인천|광주|대전|울산|수원|창원|성남|고양)",
        r"(?:미국|일본|중국|독일|영국|싱가포르|호주|캐나다)",
        r"(?:재택|원격|remote)",
    ]
}


def extract_insights(
    title: str,
    content: str,
    insight_category: InsightCategory,
    language: SourceLanguage = SourceLanguage.ENGLISH,
) -> ExtractedInsight:
    """Extract structured insights from article content.

    Args:
        title: Article title
        content: Article content
        insight_category: Classified insight category
        language: Content language

    Returns:
        ExtractedInsight object with structured data
    """
    full_text = f"{title}\n\n{content}"
    insights = ExtractedInsight(insight_category=insight_category)

    # Extract based on category
    if insight_category == InsightCategory.IN_DEMAND_SKILLS:
        insights.skills = extract_skills(full_text, language)
    elif insight_category == InsightCategory.COMPANY_NEWS:
        insights.companies = extract_companies(full_text, language)
    elif insight_category == InsightCategory.SALARY_BENEFITS:
        insights.salaries = extract_salaries(full_text, language)
    elif insight_category == InsightCategory.JOB_OPENINGS:
        insights.job_titles = extract_job_titles(full_text, language)
        insights.skills = extract_skills(full_text, language)
        insights.salaries = extract_salaries(full_text, language)
        insights.locations = extract_locations(full_text, language)
    elif insight_category == InsightCategory.HIRING_TRENDS:
        insights.companies = extract_companies(full_text, language)
        insights.quantitative_data = extract_quantitative_data(full_text, language)

    # Always extract general useful information
    if not insights.key_takeaways:
        insights.key_takeaways = extract_key_takeaways(full_text, language, insight_category)

    logger.debug(
        f"Extracted {len(insights.skills)} skills, "
        f"{len(insights.companies)} companies, "
        f"{len(insights.salaries)} salaries, "
        f"{len(insights.job_titles)} job titles, "
        f"{len(insights.locations)} locations"
    )

    return insights


def extract_skills(text: str, language: SourceLanguage) -> list[ExtractedSkill]:
    """Extract skills mentioned in text.

    Args:
        text: Text to extract from
        language: Content language

    Returns:
        List of extracted skills
    """
    skills = []
    text_lower = text.lower()

    for skill in ALL_TECH_KEYWORDS:
        # Use a simple search that works with any characters
        # We'll check if the skill appears as a substring and then validate it's not part of a longer word
        if skill.lower() in text_lower:
            # Additional check: make sure it's not part of a longer ASCII word
            # This is a heuristic - for mixed text we just check substring presence
            skill_index = text_lower.find(skill.lower())

            # Check character before skill
            before_ok = (skill_index == 0 or
                         not text_lower[skill_index - 1].isalnum() or
                         not text_lower[skill_index - 1].isascii())

            # Check character after skill
            after_index = skill_index + len(skill)
            after_ok = (after_index >= len(text_lower) or
                        not text_lower[after_index].isalnum() or
                        not text_lower[after_index].isascii())

            if before_ok and after_ok:
                # Determine skill category
                category = "general"
                if skill in PROGRAMMING_LANGUAGES:
                    category = "programming_language"
                elif skill in FRAMEWORKS:
                    category = "framework"
                elif skill in CLOUD_SERVICES:
                    category = "cloud_service"
                elif skill in DATABASES:
                    category = "database"
                elif skill in DEVOPS_TOOLS:
                    category = "devops_tool"

                # Extract context (sentence containing the skill)
                context = extract_context(text, skill)

                # Calculate relevance score based on context
                relevance = calculate_skill_relevance(context)

                skills.append(
                    ExtractedSkill(
                        skill=skill,
                        category=category,
                        context=context,
                        relevance_score=relevance,
                    )
                )

    # Remove duplicates (keeping highest relevance)
    skills = remove_duplicate_skills(skills)

    # Sort by relevance
    skills.sort(key=lambda s: s.relevance_score, reverse=True)

    return skills[:20]  # Limit to top 20 skills


def extract_companies(text: str, language: SourceLanguage) -> list[ExtractedCompany]:
    """Extract companies mentioned with context and actions.

    Args:
        text: Text to extract from
        language: Content language

    Returns:
        List of extracted companies with context
    """
    companies = []

    # Common tech company names (simplified - in production, use NER)
    tech_companies = {
        "google", "microsoft", "amazon", "apple", "meta", "facebook",
        "tesla", "netflix", "spotify", "uber", "lyft", "airbnb",
        "nvidia", "amd", "intel", "samsung", "lg", "hyundai",
        "kakao", "naver", "coupang", "toss", "baemin", "line",
        "openai", "anthropic", "stability ai", "midjourney",
        "stripe", "shopify", "square", "salesforce", "oracle",
        "ibm", "cisco", "vmware", "red hat", "docker",
    }

    text_lower = text.lower()

    for company in tech_companies:
        if company in text_lower:
            # Extract context
            context = extract_context(text, company)

            # Determine action
            action = "mentioned"
            for action_name, pattern in COMPANY_ACTIONS.items():
                if re.search(pattern, context, re.IGNORECASE):
                    action = action_name
                    break

            # Extract quantitative metrics if any
            metrics = extract_company_metrics(context)

            companies.append(
                ExtractedCompany(
                    name=company,
                    context=context,
                    action=action,
                    metrics=metrics,
                )
            )

    return companies[:10]  # Limit to top 10


def extract_salaries(text: str, language: SourceLanguage) -> list[ExtractedSalary]:
    """Extract salary information from text.

    Args:
        text: Text to extract from
        language: Content language

    Returns:
        List of extracted salaries
    """
    salaries = []

    lang_key = "english" if language == SourceLanguage.ENGLISH else "korean"
    patterns = SALARY_PATTERNS[lang_key]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            salary_text = match.group(0)
            context = extract_context(text, salary_text)

            # Parse salary amounts
            amount_min = None
            amount_max = None

            if lang_key == "english":
                # Handle English salary patterns
                numbers = re.findall(r'\$?(\d+(?:,\d+)*(?:\.\d+)?)', salary_text)
                if len(numbers) >= 1:
                    amount_min = float(numbers[0].replace(',', ''))
                if len(numbers) >= 2:
                    amount_max = float(numbers[1].replace(',', ''))

                # Convert k to thousand
                if 'k' in salary_text.lower() and amount_min:
                    amount_min *= 1000
                    if amount_max:
                        amount_max *= 1000
            else:
                # Handle Korean salary patterns
                if match.lastindex and match.lastindex >= 1:
                    num_value = match.group(1)
                    if "억원" in salary_text:
                        amount_min = float(num_value) * 100000000
                    elif "천만원" in salary_text:
                        amount_min = float(num_value) * 10000000
                    elif "만원" in salary_text:
                        amount_min = float(num_value) * 10000
                    elif "연봉" in salary_text:
                        amount_min = float(num_value)

            salaries.append(
                ExtractedSalary(
                    amount_min=amount_min,
                    amount_max=amount_max,
                    context=context,
                )
            )

    return salaries[:5]  # Limit to top 5


def extract_job_titles(text: str, language: SourceLanguage) -> list[ExtractedJobTitle]:
    """Extract job titles from text.

    Args:
        text: Text to extract from
        language: Content language

    Returns:
        List of extracted job titles
    """
    job_titles = []

    lang_key = "english" if language == SourceLanguage.ENGLISH else "korean"
    patterns = JOB_TITLE_PATTERNS[lang_key]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            title = match.group(0)
            context = extract_context(text, title)

            # Determine level
            level = SkillLevel.UNKNOWN
            if any(lvl in title.lower() for lvl in ["senior", "시니어"]):
                level = SkillLevel.SENIOR
            elif any(lvl in title.lower() for lvl in ["lead", "리드"]):
                level = SkillLevel.LEAD
            elif any(lvl in title.lower() for lvl in ["principal", "주니어"]):
                level = SkillLevel.SENIOR  # Principal is senior+
            elif any(lvl in title.lower() for lvl in ["junior", "신입", "주니어"]):
                level = SkillLevel.JUNIOR

            # Extract position count if mentioned
            count_match = re.search(r'(\d+)\s*(?:position|role|자리)', context, re.IGNORECASE)
            count = int(count_match.group(1)) if count_match else None

            job_titles.append(
                ExtractedJobTitle(
                    title=title,
                    level=level,
                    context=context,
                    count=count,
                )
            )

    # Remove duplicates
    seen = set()
    unique_titles = []
    for title in job_titles:
        title_key = title.title.lower()
        if title_key not in seen:
            seen.add(title_key)
            unique_titles.append(title)

    return unique_titles[:10]  # Limit to top 10


def extract_locations(text: str, language: SourceLanguage) -> list[ExtractedLocation]:
    """Extract locations mentioned in text.

    Args:
        text: Text to extract from
        language: Content language

    Returns:
        List of extracted locations
    """
    locations = []

    lang_key = "english" if language == SourceLanguage.ENGLISH else "korean"
    patterns = LOCATION_PATTERNS[lang_key]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Handle different match groups
            if match.lastindex and match.lastindex >= 1:
                location = match.group(1) if match.group(1) else match.group(0)
            else:
                location = match.group(0) if match.group(0) else ""

            if not location:
                continue

            context = extract_context(text, location)

            # Determine location type
            loc_type = "city"
            if re.search(r'remote|원격|재택|anywhere', location, re.IGNORECASE):
                loc_type = "remote"
            elif any(country in location.lower() for country in ["united states", "korea", "japan", "china", "미국", "한국", "일본", "중국"]):
                loc_type = "country"

            locations.append(
                ExtractedLocation(
                    location=location,
                    type=loc_type,
                    context=context,
                )
            )

    # Remove duplicates
    seen = set()
    unique_locations = []
    for loc in locations:
        loc_key = loc.location.lower()
        if loc_key not in seen:
            seen.add(loc_key)
            unique_locations.append(loc)

    return unique_locations[:5]  # Limit to top 5


def extract_key_takeaways(
    text: str,
    language: SourceLanguage,
    insight_category: InsightCategory,
    max_takeaways: int = 3,
) -> list[str]:
    """Extract key takeaways for job seekers.

    Args:
        text: Text to extract from
        language: Content language
        insight_category: Insight category
        max_takeaways: Maximum number of takeaways to extract

    Returns:
        List of key takeaway strings
    """
    takeaways = []
    sentences = re.split(r'[.!?]', text)

    # Score sentences based on job seeker relevance
    scored_sentences = []
    for sentence in sentences:
        if len(sentence.strip()) < 20:  # Skip very short sentences
            continue

        score = calculate_takeaway_score(sentence, insight_category)
        if score > 0.3:  # Only include relevant sentences
            scored_sentences.append((score, sentence.strip()))

    # Sort by score and take top N
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    takeaways = [sentence for score, sentence in scored_sentences[:max_takeaways]]

    return takeaways


def extract_quantitative_data(text: str, language: SourceLanguage) -> dict[str, Any]:
    """Extract quantitative metrics from text.

    Args:
        text: Text to extract from
        language: Content language

    Returns:
        Dictionary of quantitative metrics
    """
    data = {}

    # Extract percentages
    percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
    if percentages:
        data['percentages'] = [float(p) for p in percentages]

    # Extract large numbers (hiring counts, funding amounts, etc.)
    large_numbers = re.findall(
        r'\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|billion|k|thousand)',
        text,
        re.IGNORECASE
    )
    if large_numbers:
        data['large_numbers'] = large_numbers

    # Extract growth rates
    growth_patterns = re.findall(
        r'(?:growth|increase|decrease|rise|fall)\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*%',
        text,
        re.IGNORECASE
    )
    if growth_patterns:
        data['growth_rates'] = [float(g) for g in growth_patterns]

    return data


def extract_context(text: str, keyword: str, context_chars: int = 150) -> str:
    """Extract surrounding context for a keyword.

    Args:
        text: Full text
        keyword: Keyword to find
        context_chars: Number of characters before/after

    Returns:
        Context string
    """
    keyword_lower = keyword.lower()
    text_lower = text.lower()

    index = text_lower.find(keyword_lower)
    if index == -1:
        return ""

    start = max(0, index - context_chars)
    end = min(len(text), index + len(keyword) + context_chars)

    context = text[start:end].strip()
    return context


def calculate_skill_relevance(context: str) -> float:
    """Calculate relevance score for a skill based on context.

    Args:
        context: Context around the skill mention

    Returns:
        Relevance score 0.0-1.0
    """
    score = 0.5  # Base score

    context_lower = context.lower()

    # Boost score for high-relevance indicators
    if any(indicator in context_lower for indicator in [
        "required", "must have", "essential", "critical", "필수", "중요"
    ]):
        score += 0.3

    if any(indicator in context_lower for indicator in [
        "in demand", "hot skill", "trending", "popular", "필수스킬", "인기스킬"
    ]):
        score += 0.2

    # Lower score for low-relevance indicators
    if any(indicator in context_lower for indicator in [
        "basic", "introductory", "learn", "tutorial", "기초", "입문", "강의"
    ]):
        score -= 0.2

    return max(0.0, min(1.0, score))


def calculate_takeaway_score(sentence: str, insight_category: InsightCategory) -> float:
    """Calculate relevance score for a sentence as a takeaway.

    Args:
        sentence: Sentence to score
        insight_category: Insight category

    Returns:
        Score 0.0-1.0
    """
    score = 0.0
    sentence_lower = sentence.lower()

    # High-relevance keywords
    high_relevance = {
        InsightCategory.HIRING_TRENDS: [
            "hiring", "recruitment", "job market", "employment", "채용", "고용"
        ],
        InsightCategory.IN_DEMAND_SKILLS: [
            "in demand", "hot skill", "trending", "popular", "required",
            "인기스킬", "필수", "트렌딩"
        ],
        InsightCategory.COMPANY_NEWS: [
            "expansion", "funding", "acquisition", "ipo", "확장", "투자", "인수"
        ],
        InsightCategory.SALARY_BENEFITS: [
            "salary", "compensation", "pay", "benefits", "연봉", "보수", "복지"
        ],
        InsightCategory.CAREER_DEVELOPMENT: [
            "career growth", "advancement", "promotion", "skill development",
            "커리어성장", "진급", "스킬개발"
        ],
    }

    for keyword in high_relevance.get(insight_category, []):
        if keyword in sentence_lower:
            score += 0.2

    # Actionable indicators
    if any(indicator in sentence_lower for indicator in [
        "should", "must", "need", "require", "important", "critical",
        "해야", "필수", "중요", "필요"
    ]):
        score += 0.3

    # Quantitative information
    if re.search(r'\d+%', sentence):
        score += 0.2

    if re.search(r'\$\d+', sentence):
        score += 0.2

    return min(1.0, score)


def extract_company_metrics(context: str) -> dict[str, Union[int, float, str]]:
    """Extract quantitative metrics about a company.

    Args:
        context: Context string

    Returns:
        Dictionary of metrics
    """
    metrics = {}

    # Extract hiring numbers
    hiring_match = re.search(r'(?:hiring|recruiting)\s+(\d+)', context, re.IGNORECASE)
    if hiring_match:
        metrics["hiring_count"] = int(hiring_match.group(1))

    # Extract funding amounts
    funding_match = re.search(r'(?:raised|secured|funding)\s+\$?(\d+(?:,\d+)*)\s*(?:million|billion|mn|bn)', context, re.IGNORECASE)
    if funding_match and funding_match.lastindex and funding_match.lastindex >= 1:
        amount = funding_match.group(1).replace(',', '')
        unit = funding_match.group(2) if funding_match.lastindex >= 2 else None
        if unit and ("billion" in unit.lower() or "bn" in unit.lower()):
            amount = float(amount) * 1000000000
        else:  # million
            amount = float(amount) * 1000000
        metrics["funding_amount"] = amount

    # Extract growth percentages
    growth_match = re.search(r'(?:growth|increase)\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*%', context, re.IGNORECASE)
    if growth_match and growth_match.lastindex and growth_match.lastindex >= 1:
        metrics["growth_percentage"] = float(growth_match.group(1))

    return metrics


def remove_duplicate_skills(skills: list[ExtractedSkill]) -> list[ExtractedSkill]:
    """Remove duplicate skills, keeping the one with highest relevance.

    Args:
        skills: List of skills

    Returns:
        Deduplicated list
    """
    skill_map = {}
    for skill in skills:
        key = skill.skill.lower()
        if key not in skill_map or skill.relevance_score > skill_map[key].relevance_score:
            skill_map[key] = skill
    return list(skill_map.values())


# Export public API
__all__ = [
    "ExtractedSkill",
    "ExtractedCompany",
    "ExtractedSalary",
    "ExtractedJobTitle",
    "ExtractedLocation",
    "ExtractedInsight",
    "SkillLevel",
    "extract_insights",
    "extract_skills",
    "extract_companies",
    "extract_salaries",
    "extract_job_titles",
    "extract_locations",
    "extract_key_takeaways",
    "extract_quantitative_data",
]
