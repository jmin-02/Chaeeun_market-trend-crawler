"""Discord embed builder and template system.

This module provides a fluent API for creating rich Discord embeds with
validation and pre-built templates for common use cases.

Features:
- Fluent builder pattern for easy embed creation
- Embed field builder
- Pre-built templates (article, report, insight)
- Embed validation against Discord limits
- Color presets for different categories
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from .models import Article, Category, SourceLanguage

logger = logging.getLogger(__name__)


# Discord embed limits
MAX_EMBEDS = 10
MAX_EMBED_TITLE_LENGTH = 256
MAX_EMBED_DESCRIPTION_LENGTH = 4096
MAX_EMBED_FIELDS = 25
MAX_EMBED_FIELD_NAME_LENGTH = 256
MAX_EMBED_FIELD_VALUE_LENGTH = 1024
MAX_EMBED_FOOTER_TEXT_LENGTH = 2048
MAX_EMBED_AUTHOR_NAME_LENGTH = 256


class EmbedColor(Enum):
    """Pre-defined colors for Discord embeds.

    Discord accepts:
    - Integer color values (0x000000 to 0xFFFFFF)
    - Hex color strings
    - Color names
    """

    # Category colors
    AI_ML = 0x7289DA  # Blurple
    BLOCKCHAIN_WEB3 = 0xF47B67  # Coral
    STARTUP_BUSINESS = 0x43B581  # Green
    TECH_PRODUCTS = 0xFAA61A  # Orange
    DEVOPS_CLOUD = 0x3BA55D  # Green
    OTHER = 0x99AAB5  # Grey

    # Status colors
    SUCCESS = 0x43B581  # Green
    WARNING = 0xFAA61A  # Orange
    ERROR = 0xF04747  # Red
    INFO = 0x7289DA  # Blurple

    # Special colors
    BLUE = 0x3498DB
    PURPLE = 0x9B59B6
    GOLD = 0xF1C40F
    TEAL = 0x1ABC9C
    PINK = 0xE91E63


@dataclass
class EmbedField:
    """Discord embed field.

    Attributes:
        name: Field name (max 256 chars)
        value: Field value (max 1024 chars)
        inline: Whether field should be displayed inline
    """

    name: str
    value: str
    inline: bool = False

    def __post_init__(self):
        """Validate field after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Field name cannot be empty")

        if not self.value or not self.value.strip():
            raise ValueError("Field value cannot be empty")

        if len(self.name) > MAX_EMBED_FIELD_NAME_LENGTH:
            logger.warning(
                f"Field name exceeds Discord limit: {len(self.name)} > {MAX_EMBED_FIELD_NAME_LENGTH}"
            )

        if len(self.value) > MAX_EMBED_FIELD_VALUE_LENGTH:
            logger.warning(
                f"Field value exceeds Discord limit: {len(self.value)} > {MAX_EMBED_FIELD_VALUE_LENGTH}"
            )


@dataclass
class EmbedFooter:
    """Discord embed footer.

    Attributes:
        text: Footer text (max 2048 chars)
        icon_url: URL to footer icon
    """

    text: str
    icon_url: Optional[str] = None

    def __post_init__(self):
        """Validate footer after initialization."""
        if len(self.text) > MAX_EMBED_FOOTER_TEXT_LENGTH:
            logger.warning(
                f"Footer text exceeds Discord limit: {len(self.text)} > {MAX_EMBED_FOOTER_TEXT_LENGTH}"
            )


@dataclass
class EmbedAuthor:
    """Discord embed author.

    Attributes:
        name: Author name (max 256 chars)
        url: URL to author's page
        icon_url: URL to author's icon
    """

    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None

    def __post_init__(self):
        """Validate author after initialization."""
        if len(self.name) > MAX_EMBED_AUTHOR_NAME_LENGTH:
            logger.warning(
                f"Author name exceeds Discord limit: {len(self.name)} > {MAX_EMBED_AUTHOR_NAME_LENGTH}"
            )


@dataclass
class EmbedThumbnail:
    """Discord embed thumbnail.

    Attributes:
        url: URL to thumbnail image
    """

    url: str


@dataclass
class EmbedImage:
    """Discord embed image.

    Attributes:
        url: URL to image
    """

    url: str


class EmbedBuilder:
    """Fluent builder for creating Discord embeds.

    Usage:
        builder = EmbedBuilder(title="Article Title")
        builder.description("This is the description")
        builder.color(EmbedColor.AI_ML)
        builder.add_field("Field 1", "Value 1", inline=True)
        builder.add_field("Field 2", "Value 2", inline=True)
        embed = builder.build()
    """

    def __init__(self, title: str):
        """Initialize embed builder.

        Args:
            title: Embed title (required)
        """
        self._title = title
        self._description: Optional[str] = None
        self._color: Optional[int] = None
        self._fields: list[EmbedField] = []
        self._footer: Optional[EmbedFooter] = None
        self._author: Optional[EmbedAuthor] = None
        self._thumbnail: Optional[EmbedThumbnail] = None
        self._image: Optional[EmbedImage] = None
        self._timestamp: Optional[datetime] = None
        self._url: Optional[str] = None

    def description(self, text: str) -> "EmbedBuilder":
        """Set embed description.

        Args:
            text: Description text (max 4096 chars)

        Returns:
            Self for chaining
        """
        if len(text) > MAX_EMBED_DESCRIPTION_LENGTH:
            logger.warning(
                f"Description exceeds Discord limit: {len(text)} > {MAX_EMBED_DESCRIPTION_LENGTH}"
            )
        self._description = text
        return self

    def color(self, color: Union[int, EmbedColor, str]) -> "EmbedBuilder":
        """Set embed color.

        Args:
            color: Color value (int, EmbedColor enum, or hex string)

        Returns:
            Self for chaining
        """
        if isinstance(color, EmbedColor):
            self._color = color.value
        elif isinstance(color, str):
            # Parse hex color string
            if color.startswith("#"):
                color = color[1:]
            self._color = int(color, 16)
        else:
            self._color = color
        return self

    def add_field(
        self,
        name: str,
        value: str,
        inline: bool = False
    ) -> "EmbedBuilder":
        """Add a field to the embed.

        Args:
            name: Field name
            value: Field value
            inline: Whether field should be inline

        Returns:
            Self for chaining
        """
        if len(self._fields) >= MAX_EMBED_FIELDS:
            logger.warning(
                f"Cannot add more fields: maximum of {MAX_EMBED_FIELDS} reached"
            )
            return self

        field = EmbedField(name=name, value=value, inline=inline)
        self._fields.append(field)
        return self

    def add_fields(
        self,
        fields: list[tuple[str, str, bool]]
    ) -> "EmbedBuilder":
        """Add multiple fields to the embed.

        Args:
            fields: List of (name, value, inline) tuples

        Returns:
            Self for chaining
        """
        for name, value, inline in fields:
            self.add_field(name, value, inline)
        return self

    def footer(
        self,
        text: str,
        icon_url: Optional[str] = None
    ) -> "EmbedBuilder":
        """Set embed footer.

        Args:
            text: Footer text
            icon_url: URL to footer icon

        Returns:
            Self for chaining
        """
        self._footer = EmbedFooter(text=text, icon_url=icon_url)
        return self

    def author(
        self,
        name: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None
    ) -> "EmbedBuilder":
        """Set embed author.

        Args:
            name: Author name
            url: URL to author's page
            icon_url: URL to author's icon

        Returns:
            Self for chaining
        """
        self._author = EmbedAuthor(name=name, url=url, icon_url=icon_url)
        return self

    def thumbnail(self, url: str) -> "EmbedBuilder":
        """Set embed thumbnail.

        Args:
            url: URL to thumbnail image

        Returns:
            Self for chaining
        """
        self._thumbnail = EmbedThumbnail(url=url)
        return self

    def image(self, url: str) -> "EmbedBuilder":
        """Set embed image.

        Args:
            url: URL to image

        Returns:
            Self for chaining
        """
        self._image = EmbedImage(url=url)
        return self

    def timestamp(self, ts: datetime) -> "EmbedBuilder":
        """Set embed timestamp.

        Args:
            ts: Timestamp for the embed

        Returns:
            Self for chaining
        """
        self._timestamp = ts
        return self

    def url(self, url: str) -> "EmbedBuilder":
        """Set embed URL.

        Args:
            url: URL for the embed title

        Returns:
            Self for chaining
        """
        self._url = url
        return self

    def build(self) -> dict:
        """Build the embed dictionary.

        Returns:
            Discord embed dictionary ready to use
        """
        embed = {
            "title": self._title,
        }

        if self._description:
            embed["description"] = self._description

        if self._color:
            embed["color"] = self._color

        if self._fields:
            embed["fields"] = [
                {"name": f.name, "value": f.value, "inline": f.inline}
                for f in self._fields
            ]

        if self._footer:
            embed["footer"] = {
                "text": self._footer.text,
            }
            if self._footer.icon_url:
                embed["footer"]["icon_url"] = self._footer.icon_url

        if self._author:
            embed["author"] = {
                "name": self._author.name,
            }
            if self._author.url:
                embed["author"]["url"] = self._author.url
            if self._author.icon_url:
                embed["author"]["icon_url"] = self._author.icon_url

        if self._thumbnail:
            embed["thumbnail"] = {"url": self._thumbnail.url}

        if self._image:
            embed["image"] = {"url": self._image.url}

        if self._timestamp:
            embed["timestamp"] = self._timestamp.isoformat()

        if self._url:
            embed["url"] = self._url

        return embed

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the embed.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate title
        if not self._title:
            errors.append("Title cannot be empty")
        elif len(self._title) > MAX_EMBED_TITLE_LENGTH:
            errors.append(
                f"Title exceeds limit: {len(self._title)} > {MAX_EMBED_TITLE_LENGTH}"
            )

        # Validate description
        if self._description and len(self._description) > MAX_EMBED_DESCRIPTION_LENGTH:
            errors.append(
                f"Description exceeds limit: {len(self._description)} > {MAX_EMBED_DESCRIPTION_LENGTH}"
            )

        # Validate fields
        if len(self._fields) > MAX_EMBED_FIELDS:
            errors.append(
                f"Too many fields: {len(self._fields)} > {MAX_EMBED_FIELDS}"
            )

        for i, field in enumerate(self._fields):
            if len(field.name) > MAX_EMBED_FIELD_NAME_LENGTH:
                errors.append(
                    f"Field {i} name exceeds limit: {len(field.name)} > {MAX_EMBED_FIELD_NAME_LENGTH}"
                )
            if len(field.value) > MAX_EMBED_FIELD_VALUE_LENGTH:
                errors.append(
                    f"Field {i} value exceeds limit: {len(field.value)} > {MAX_EMBED_FIELD_VALUE_LENGTH}"
                )

        # Validate footer
        if self._footer and len(self._footer.text) > MAX_EMBED_FOOTER_TEXT_LENGTH:
            errors.append(
                f"Footer text exceeds limit: {len(self._footer.text)} > {MAX_EMBED_FOOTER_TEXT_LENGTH}"
            )

        # Validate author
        if self._author and len(self._author.name) > MAX_EMBED_AUTHOR_NAME_LENGTH:
            errors.append(
                f"Author name exceeds limit: {len(self._author.name)} > {MAX_EMBED_AUTHOR_NAME_LENGTH}"
            )

        return len(errors) == 0, errors


def validate_embeds(embeds: list[dict]) -> tuple[bool, list[str]]:
    """Validate a list of embeds.

    Args:
        embeds: List of embed dictionaries

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check embed count
    if len(embeds) > MAX_EMBEDS:
        errors.append(
            f"Too many embeds: {len(embeds)} > {MAX_EMBEDS}"
        )
        return False, errors

    # Validate each embed
    for i, embed in enumerate(embeds):
        # Check title
        title = embed.get("title", "")
        if title and len(title) > MAX_EMBED_TITLE_LENGTH:
            errors.append(
                f"Embed {i} title exceeds limit: {len(title)} > {MAX_EMBED_TITLE_LENGTH}"
            )

        # Check description
        description = embed.get("description", "")
        if description and len(description) > MAX_EMBED_DESCRIPTION_LENGTH:
            errors.append(
                f"Embed {i} description exceeds limit: {len(description)} > {MAX_EMBED_DESCRIPTION_LENGTH}"
            )

        # Check fields
        fields = embed.get("fields", [])
        if len(fields) > MAX_EMBED_FIELDS:
            errors.append(
                f"Embed {i} has too many fields: {len(fields)} > {MAX_EMBED_FIELDS}"
            )

        for j, field in enumerate(fields):
            name = field.get("name", "")
            value = field.get("value", "")

            if name and len(name) > MAX_EMBED_FIELD_NAME_LENGTH:
                errors.append(
                    f"Embed {i} field {j} name exceeds limit: {len(name)} > {MAX_EMBED_FIELD_NAME_LENGTH}"
                )

            if value and len(value) > MAX_EMBED_FIELD_VALUE_LENGTH:
                errors.append(
                    f"Embed {i} field {j} value exceeds limit: {len(value)} > {MAX_EMBED_FIELD_VALUE_LENGTH}"
                )

        # Check footer
        footer = embed.get("footer", {})
        footer_text = footer.get("text", "")
        if footer_text and len(footer_text) > MAX_EMBED_FOOTER_TEXT_LENGTH:
            errors.append(
                f"Embed {i} footer text exceeds limit: {len(footer_text)} > {MAX_EMBED_FOOTER_TEXT_LENGTH}"
            )

        # Check author
        author = embed.get("author", {})
        author_name = author.get("name", "")
        if author_name and len(author_name) > MAX_EMBED_AUTHOR_NAME_LENGTH:
            errors.append(
                f"Embed {i} author name exceeds limit: {len(author_name)} > {MAX_EMBED_AUTHOR_NAME_LENGTH}"
            )

    return len(errors) == 0, errors


# ============================================================================
# EMBED TEMPLATES
# ============================================================================

def create_article_embed(
    article: Article,
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> dict:
    """Create a Discord embed for an article.

    Args:
        article: Article to create embed for
        language: Language for labels (Korean or English)

    Returns:
        Discord embed dictionary
    """
    # Get color based on category
    color_map = {
        Category.AI_ML: EmbedColor.AI_ML,
        Category.BLOCKCHAIN_WEB3: EmbedColor.BLOCKCHAIN_WEB3,
        Category.STARTUP_BUSINESS: EmbedColor.STARTUP_BUSINESS,
        Category.TECH_PRODUCTS: EmbedColor.TECH_PRODUCTS,
        Category.DEVOPS_CLOUD: EmbedColor.DEVOPS_CLOUD,
        Category.OTHER: EmbedColor.OTHER,
    }
    color = color_map.get(article.category, EmbedColor.OTHER)

    # Language flag emoji
    flag = "🇰🇷" if article.language == SourceLanguage.KOREAN else "🇺🇸"

    # Create embed
    builder = EmbedBuilder(
        title=f"{article.title} {flag}"
    )
    builder.url(str(article.url))
    builder.color(color)

    # Add description (summary or truncated content)
    description = article.summary or article.content
    if len(description) > 2000:
        description = description[:2000] + "..."
    builder.description(description)

    # Add fields
    source_label = "소스" if language == SourceLanguage.KOREAN else "Source"
    category_label = "카테고리" if language == SourceLanguage.KOREAN else "Category"

    builder.add_field(source_label, article.source, inline=True)
    builder.add_field(category_label, article.category.value, inline=True)

    if article.tags:
        tags_label = "태그" if language == SourceLanguage.KOREAN else "Tags"
        tags_text = ", ".join(article.tags[:5])
        builder.add_field(tags_label, tags_text, inline=False)

    # Add footer with publication time
    if article.published_at:
        pub_time = article.published_at.strftime("%Y-%m-%d %H:%M")
        footer_text = f"Published: {pub_time} | {article.source}"
    else:
        footer_text = f"{article.source}"

    builder.footer(footer_text)

    # Add timestamp
    if article.published_at:
        builder.timestamp(article.published_at)

    return builder.build()


def create_summary_embed(
    total_articles: int,
    period_start: datetime,
    period_end: datetime,
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> dict:
    """Create a summary embed for a report.

    Args:
        total_articles: Total number of articles
        period_start: Start date of the period
        period_end: End date of the period
        language: Language for labels (Korean or English)

    Returns:
        Discord embed dictionary
    """
    if language == SourceLanguage.KOREAN:
        title = "📋 주간 요약"
        description = f"기간: {period_start.strftime('%Y-%m-%d')} ~ {period_end.strftime('%Y-%m-%d')}"
        footer = f"총 {total_articles}개 기사 | Ouroboros AI"
    else:
        title = "📋 Weekly Summary"
        description = f"Period: {period_start.strftime('%Y-%m-%d')} ~ {period_end.strftime('%Y-%m-%d')}"
        footer = f"{total_articles} articles total | Ouroboros AI"

    builder = EmbedBuilder(title=title)
    builder.description(description)
    builder.color(EmbedColor.INFO)
    builder.footer(footer)
    builder.timestamp(datetime.now())

    return builder.build()


def create_category_summary_embed(
    category: Category,
    count: int,
    percentage: float,
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> dict:
    """Create a category summary embed.

    Args:
        category: Category to summarize
        count: Number of articles in category
        percentage: Percentage of total articles
        language: Language for labels (Korean or English)

    Returns:
        Discord embed dictionary
    """
    # Get color based on category
    color_map = {
        Category.AI_ML: EmbedColor.AI_ML,
        Category.BLOCKCHAIN_WEB3: EmbedColor.BLOCKCHAIN_WEB3,
        Category.STARTUP_BUSINESS: EmbedColor.STARTUP_BUSINESS,
        Category.TECH_PRODUCTS: EmbedColor.TECH_PRODUCTS,
        Category.DEVOPS_CLOUD: EmbedColor.DEVOPS_CLOUD,
        Category.OTHER: EmbedColor.OTHER,
    }
    color = color_map.get(category, EmbedColor.OTHER)

    # Category emoji
    emoji_map = {
        Category.AI_ML: "🤖",
        Category.BLOCKCHAIN_WEB3: "⛓️",
        Category.STARTUP_BUSINESS: "🚀",
        Category.TECH_PRODUCTS: "📱",
        Category.DEVOPS_CLOUD: "☁️",
        Category.OTHER: "📰",
    }
    emoji = emoji_map.get(category, "📰")

    if language == SourceLanguage.KOREAN:
        title = f"{emoji} {category.value.replace('_', ' ')}"
        description = f"{count}개 기사 ({percentage:.1f}%)"
    else:
        title = f"{emoji} {category.value.replace('_', ' ')}"
        description = f"{count} articles ({percentage:.1f}%)"

    builder = EmbedBuilder(title=title)
    builder.description(description)
    builder.color(color)

    return builder.build()


def create_insight_embed(
    insight_type: str,
    count: int,
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> dict:
    """Create an insight summary embed.

    Args:
        insight_type: Type of insight (e.g., "Skills", "Companies")
        count: Number of insights
        language: Language for labels (Korean or English)

    Returns:
        Discord embed dictionary
    """
    if language == SourceLanguage.KOREAN:
        title = f"💡 {insight_type}"
        description = f"총 {count}개 항목"
    else:
        title = f"💡 {insight_type}"
        description = f"Total: {count} items"

    builder = EmbedBuilder(title=title)
    builder.description(description)
    builder.color(EmbedColor.PURPLE)
    builder.footer("Job Seeker Insights")

    return builder.build()


def create_error_embed(
    error_message: str,
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> dict:
    """Create an error embed.

    Args:
        error_message: Error message to display
        language: Language for labels (Korean or English)

    Returns:
        Discord embed dictionary
    """
    if language == SourceLanguage.KOREAN:
        title = "❌ 오류 발생"
        description = error_message
        footer = "문제가 지속되면 관리자에게 문의하세요"
    else:
        title = "❌ Error Occurred"
        description = error_message
        footer = "If the problem persists, please contact support"

    builder = EmbedBuilder(title=title)
    builder.description(description)
    builder.color(EmbedColor.ERROR)
    builder.footer(footer)
    builder.timestamp(datetime.now())

    return builder.build()


def create_success_embed(
    message: str,
    language: SourceLanguage = SourceLanguage.ENGLISH
) -> dict:
    """Create a success embed.

    Args:
        message: Success message to display
        language: Language for labels (Korean or English)

    Returns:
        Discord embed dictionary
    """
    if language == SourceLanguage.KOREAN:
        title = "✅ 성공"
        description = message
        footer = "Ouroboros AI"
    else:
        title = "✅ Success"
        description = message
        footer = "Ouroboros AI"

    builder = EmbedBuilder(title=title)
    builder.description(message)
    builder.color(EmbedColor.SUCCESS)
    builder.footer(footer)
    builder.timestamp(datetime.now())

    return builder.build()


# Export public API
__all__ = [
    # Limits
    "MAX_EMBEDS",
    "MAX_EMBED_TITLE_LENGTH",
    "MAX_EMBED_DESCRIPTION_LENGTH",
    "MAX_EMBED_FIELDS",
    "MAX_EMBED_FIELD_NAME_LENGTH",
    "MAX_EMBED_FIELD_VALUE_LENGTH",
    "MAX_EMBED_FOOTER_TEXT_LENGTH",
    "MAX_EMBED_AUTHOR_NAME_LENGTH",
    # Classes
    "EmbedColor",
    "EmbedField",
    "EmbedFooter",
    "EmbedAuthor",
    "EmbedThumbnail",
    "EmbedImage",
    "EmbedBuilder",
    # Functions
    "validate_embeds",
    # Templates
    "create_article_embed",
    "create_summary_embed",
    "create_category_summary_embed",
    "create_insight_embed",
    "create_error_embed",
    "create_success_embed",
]
