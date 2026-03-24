"""Centralized classification utility for 5-category tech news classification.

This module provides keyword-based classification for tech news articles
into 5 consolidated categories: AI_ML, BLOCKCHAIN_WEB3, STARTUP_BUSINESS,
TECH_PRODUCTS, and DEVOPS_CLOUD.

The classification is based on keyword matching in URLs and titles, supporting
both Korean and English keywords.
"""

import logging
import re
from typing import Optional

from .models import Category

logger = logging.getLogger(__name__)


# Consolidated category keywords mapping
# Each category consolidates multiple subcategories from the original 11-category system
CATEGORY_KEYWORDS = {
    Category.AI_ML: {
        "english": [
            "ai", "artificial intelligence", "machine learning", "llm", "chatgpt",
            "gpt", "neural network", "deep learning", "nlp", "computer vision",
            "generative ai", "transformer", "bert", "diffusion", "stable diffusion"
        ],
        "korean": [
            "인공지능", "머신러닝", "딥러닝", "llm", "챗gpt", "신경망",
            "자연어처리", "컴퓨터비전", "생성형ai", "트랜스포머"
        ]
    },
    Category.BLOCKCHAIN_WEB3: {
        "english": [
            "blockchain", "web3", "crypto", "cryptocurrency", "bitcoin", "ethereum",
            "nft", "metaverse", "defi", "dao", "smart contract", "solana",
            "polkadot", "avalanche", "coin", "token", "wallet", "defi"
        ],
        "korean": [
            "블록체인", "web3", "암호화폐", "비트코인", "이더리움", "nft",
            "메타버스", "defi", "디파이", "스마트컨트랙트", "코인", "토큰", "지갑"
        ]
    },
    Category.STARTUP_BUSINESS: {
        "english": [
            "startup", "venture", "funding", "ipo", "series a", "series b",
            "y combinator", "vc", "angel investor", "accelerator", "silicon valley",
            "investment", "venture capital", "seed funding", "unicorn", "exit",
            "acquisition", "merger", "valuation", "investment round"
        ],
        "korean": [
            "스타트업", "벤처", "투자", "ipo", "시리즈a", "시리즈b",
            "vc", "벤처캐피털", "앤젤투자", "엑셀러레이터", "시드투자",
            "유니콘", "엑싯", "인수", "합병", "밸류에이션", "투자라운드"
        ]
    },
    Category.TECH_PRODUCTS: {
        "english": [
            # Hardware keywords
            "hardware", "semiconductor", "chip", "processor", "cpu", "gpu",
            "review", "gadget", "pc", "laptop", "desktop", "component",
            # Mobile keywords
            "mobile", "smartphone", "iphone", "android", "ios", "app",
            "tablet", "5g", "wireless", "cellular", "samsung galaxy",
            # Productivity keywords
            "productivity", "product", "review", "tool", "efficiency",
            "workflow", "automation", "synchronization", "app review",
            "software review", "gaming", "console", "playstation", "xbox"
        ],
        "korean": [
            # Hardware keywords
            "반도체", "칩", "프로세서", "cpu", "gpu", "하드웨어",
            "리뷰", "기기", "pc", "노트북", "데스크탑", "부품",
            # Mobile keywords
            "모바일", "스마트폰", "아이폰", "안드로이드", "ios", "앱",
            "태블릿", "5g", "무선", "셀룰러", "갤럭시",
            # Productivity keywords
            "생산성", "제품", "리뷰", "도구", "효율성",
            "워크플로우", "자동화", "동기화", "앱리뷰",
            "소프트웨어리뷰", "게이밍", "콘솔", "플레이스테이션", "엑스박스"
        ]
    },
    Category.DEVOPS_CLOUD: {
        "english": [
            # Development keywords
            "development", "developer", "programming", "code", "software",
            "engineering", "api", "frontend", "backend", "fullstack", "devops",
            "coding", "debug", "git", "version control", "framework",
            "python", "javascript", "java", "golang", "rust", "typescript",
            # Cloud keywords
            "cloud", "aws", "azure", "gcp", "server", "saas", "paas", "iaas",
            "kubernetes", "docker", "virtualization", "hosting", "infrastructure",
            "serverless", "microservices", "container", "orchestration",
            # Security keywords
            "security", "hack", "breach", "privacy", "cyber", "cybersecurity",
            "malware", "phishing", "ransomware", "vulnerability", "penetration testing",
            # Data keywords
            "data", "analytics", "big data", "database", "sql", "nosql",
            "data science", "data engineering", "business intelligence", "data warehouse"
        ],
        "korean": [
            # Development keywords
            "개발", "개발자", "프로그래밍", "코드", "소프트웨어",
            "엔지니어링", "api", "프론트엔드", "백엔드", "풀스택", "데브옵스",
            "코딩", "디버그", "버전관리", "프레임워크",
            "파이썬", "자바스크립트", "자바", "고랭", "러스트", "타입스크립트",
            # Cloud keywords
            "클라우드", "aws", "azure", "gcp", "서버", "saas", "paas", "iaas",
            "쿠버네티스", "도커", "가상화", "호스팅", "인프라",
            "서버리스", "마이크로서비스", "컨테이너", "오케스트레이션",
            # Security keywords
            "보안", "해킹", "유출", "프라이버시", "사이버", "사이버보안",
            "멀웨어", "피싱", "랜섬웨어", "취약점", "침투테스트",
            # Data keywords
            "데이터", "분석", "빅데이터", "데이터베이스", "sql", "nosql",
            "데이터사이언스", "데이터엔지니어링", "비즈니스인텔리전스", "데이터웨어하우스"
        ]
    }
}


def classify_article(url: str, title: str, content: Optional[str] = None) -> Category:
    """Classify an article into one of 5 categories based on keyword matching.

    This function checks for category-specific keywords in the URL and title.
    Content can be optionally provided for additional context.

    Args:
        url: Article URL
        title: Article title
        content: Optional article content for additional context

    Returns:
        Detected category (defaults to Category.OTHER if no match)
    """
    url_lower = url.lower()
    title_lower = title.lower()
    content_lower = content.lower() if content else ""

    # Combine searchable text
    searchable_text = f"{url_lower} {title_lower} {content_lower}"

    # Check each category's keywords
    for category, keywords_dict in CATEGORY_KEYWORDS.items():
        if category == Category.OTHER:
            continue

        # Check English keywords
        for keyword in keywords_dict["english"]:
            if _contains_keyword(keyword, searchable_text):
                logger.debug(f"Classified as {category}: matched English keyword '{keyword}'")
                return category

        # Check Korean keywords
        for keyword in keywords_dict["korean"]:
            if _contains_keyword(keyword, searchable_text):
                logger.debug(f"Classified as {category}: matched Korean keyword '{keyword}'")
                return category

    # Default to OTHER if no category matches
    logger.debug("No category match, defaulting to OTHER")
    return Category.OTHER


def _contains_keyword(keyword: str, text: str) -> bool:
    """Check if a keyword appears in text with proper word boundary matching.

    Args:
        keyword: Keyword to search for
        text: Text to search in

    Returns:
        True if keyword is found, False otherwise
    """
    # For multi-word keywords, check exact phrase match
    if " " in keyword:
        return keyword in text

    # For single-word keywords, check word boundary matching
    # This prevents matching "app" in "apple" or "api" in "capable"
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return re.search(pattern, text) is not None


def get_category_keywords(category: Category) -> dict[str, list[str]]:
    """Get all keywords associated with a category.

    Args:
        category: Category enum value

    Returns:
        Dictionary with "english" and "korean" keyword lists
    """
    if category in CATEGORY_KEYWORDS:
        return CATEGORY_KEYWORDS[category]
    return {"english": [], "korean": []}


def get_category_description(category: Category) -> str:
    """Get a human-readable description for a category.

    Args:
        category: Category enum value

    Returns:
        Category description string
    """
    descriptions = {
        Category.AI_ML: "Artificial Intelligence and Machine Learning",
        Category.BLOCKCHAIN_WEB3: "Blockchain, Web3, and Cryptocurrency",
        Category.STARTUP_BUSINESS: "Startups, Venture Capital, and Investment",
        Category.TECH_PRODUCTS: "Technology Products, Hardware, and Consumer Tech",
        Category.DEVOPS_CLOUD: "Development, Cloud, Security, and Data Infrastructure",
        Category.OTHER: "Other Technology Topics"
    }
    return descriptions.get(category, "Unknown Category")


def map_legacy_category(legacy_category: str) -> Category:
    """Map legacy 11-category system to new 5-category system.

    This is useful for backward compatibility when migrating from the old system.

    Args:
        legacy_category: Legacy category name string

    Returns:
        Mapped Category enum value
    """
    mapping = {
        "AI_ML": Category.AI_ML,
        "WEB3_BLOCKCHAIN": Category.BLOCKCHAIN_WEB3,
        "STARTUP": Category.STARTUP_BUSINESS,
        "DEVELOPMENT": Category.DEVOPS_CLOUD,
        "SECURITY": Category.DEVOPS_CLOUD,
        "CLOUD": Category.DEVOPS_CLOUD,
        "DATA": Category.DEVOPS_CLOUD,
        "HARDWARE": Category.TECH_PRODUCTS,
        "MOBILE": Category.TECH_PRODUCTS,
        "PRODUCTIVITY": Category.TECH_PRODUCTS,
        "OTHER": Category.OTHER
    }
    return mapping.get(legacy_category, Category.OTHER)


# Export public API
__all__ = [
    "classify_article",
    "get_category_keywords",
    "get_category_description",
    "map_legacy_category",
    "CATEGORY_KEYWORDS",
]
