"""Data models for crawler framework."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, HttpUrl


class Category(str, Enum):
    """Article categories for classification (5 consolidated categories)."""

    AI_ML = "AI_ML"
    BLOCKCHAIN_WEB3 = "BLOCKCHAIN_WEB3"
    STARTUP_BUSINESS = "STARTUP_BUSINESS"
    TECH_PRODUCTS = "TECH_PRODUCTS"
    DEVOPS_CLOUD = "DEVOPS_CLOUD"
    OTHER = "OTHER"


class InsightCategory(str, Enum):
    """Insight categories for job seeker value analysis."""

    HIRING_TRENDS = "HIRING_TRENDS"
    IN_DEMAND_SKILLS = "IN_DEMAND_SKILLS"
    COMPANY_NEWS = "COMPANY_NEWS"
    SALARY_BENEFITS = "SALARY_BENEFITS"
    CAREER_DEVELOPMENT = "CAREER_DEVELOPMENT"
    JOB_OPENINGS = "JOB_OPENINGS"
    INDUSTRY_OUTLOOK = "INDUSTRY_OUTLOOK"
    TECH_UPDATES = "TECH_UPDATES"
    WORKPLACE_CULTURE = "WORKPLACE_CULTURE"
    EDUCATION_TRAINING = "EDUCATION_TRAINING"
    OTHER = "OTHER"


class SourceLanguage(str, Enum):
    """Source content language."""

    KOREAN = "ko"
    ENGLISH = "en"


@dataclass
class Source:
    """Source site configuration for crawling."""

    name: str
    url: str
    language: SourceLanguage
    category_mapping: dict[str, Category] = field(default_factory=dict)
    enabled: bool = True


class Article(BaseModel):
    """Article model for crawled content."""

    title: str
    url: HttpUrl
    content: str
    summary: Optional[str] = None
    category: Category = Category.OTHER
    insight_category: Union[InsightCategory, str] = InsightCategory.OTHER
    source: str
    published_at: datetime
    crawled_at: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    language: SourceLanguage = SourceLanguage.ENGLISH

    def is_fresh(self, hours: int = 24) -> bool:
        """Check if article is within specified hours."""
        delta = datetime.now() - self.crawled_at
        return delta.total_seconds() <= hours * 3600

    def validate(self) -> tuple[bool, list[str]]:
        """Validate article data.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate required fields
        if not self.title or len(self.title) < 5:
            errors.append(f"Invalid title: '{self.title}'")

        if not self.content or len(self.content) < 10:
            errors.append(f"Invalid content: length={len(self.content) if self.content else 0}")

        if not self.url or not str(self.url).startswith(("http://", "https://")):
            errors.append(f"Invalid URL: '{self.url}'")

        # Validate category
        if not isinstance(self.category, Category):
            errors.append(f"Invalid category: '{self.category}'")

        # Validate insight_category (can be enum or string)
        if self.insight_category:
            if not isinstance(self.insight_category, (InsightCategory, str)):
                errors.append(f"Invalid insight_category: '{self.insight_category}'")
        else:
            # Default to OTHER if not set
            self.insight_category = InsightCategory.OTHER

        # Validate source
        if not self.source or len(self.source) < 2:
            errors.append(f"Invalid source: '{self.source}'")

        # Validate language
        if not isinstance(self.language, SourceLanguage):
            errors.append(f"Invalid language: '{self.language}'")

        # Validate datetime
        if not isinstance(self.published_at, datetime):
            errors.append(f"Invalid published_at: '{self.published_at}'")

        # Validate tags
        if not isinstance(self.tags, list):
            errors.append(f"Invalid tags: not a list")
        elif len(self.tags) > 50:
            errors.append(f"Too many tags: {len(self.tags)}")

        return len(errors) == 0, errors

    def to_dict(self) -> dict:
        """Convert article to dictionary.

        Returns:
            Dictionary representation of article
        """
        return {
            "title": self.title,
            "url": str(self.url),
            "content": self.content,
            "summary": self.summary,
            "category": self.category.value if isinstance(self.category, Category) else self.category,
            "insight_category": (
                self.insight_category.value if isinstance(self.insight_category, InsightCategory)
                else self.insight_category
            ),
            "source": self.source,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "crawled_at": self.crawled_at.isoformat() if self.crawled_at else None,
            "author": self.author,
            "tags": self.tags,
            "language": self.language.value if isinstance(self.language, SourceLanguage) else self.language,
            "is_fresh": self.is_fresh(24),
        }

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v),
        }
