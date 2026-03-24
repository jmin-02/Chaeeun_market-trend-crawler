"""Insight categorization module for job seeker-focused tech news analysis.

This module provides insight categorization for tech news articles,
focusing on information valuable to job seekers such as hiring trends,
in-demand skills, company news, salary/benefits, and more.

The insight categories are distinct from content categories (AI_ML, etc.)
and focus on the *relevance* to job seekers rather than the *topic*.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class InsightCategory(str):
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


# Insight category keywords mapping
# Each category focuses on job seeker value rather than technical content
INSIGHT_KEYWORDS = {
    InsightCategory.HIRING_TRENDS: {
        "english": [
            # Hiring volume and patterns
            "hiring", "recruiting", "recruitment", "job market", "employment",
            "workforce", "talent acquisition", "headcount", "layoff", "firing",
            "hiring freeze", "hiring spree", "hiring boom", "job cuts",
            # Market trends
            "talent shortage", "talent crunch", "skill shortage", "labor market",
            "unemployment", "employment rate", "job growth", "job creation",
            "workforce reduction", "staffing", "workforce planning",
            # Seasonal/cyclical patterns
            "seasonal hiring", "quarterly hiring", "annual hiring report",
            # Company hiring patterns
            "aggressive hiring", "slow hiring", "ramping up hiring",
            "mass hiring", "bulk hiring", "hiring slowdown"
        ],
        "korean": [
            # Hiring volume and patterns
            "채용", "구인", "채용시장", "고용", "인력", "인력충원", "감원",
            "채용중단", "채용확대", "대규모채용", "해고", "정리해고",
            # Market trends
            "인력난", "인력부족", "스킬부족", "노동시장", "실업률",
            "고용률", "일자리증가", "취업률", "인력감축", "인력계획",
            # Seasonal/cyclical patterns
            "계절적채용", "분기별채용", "연간채용현황",
            # Company hiring patterns
            "공격적채용", "채용둔화", "채용가속", "대량채용", "채용감속"
        ]
    },

    InsightCategory.IN_DEMAND_SKILLS: {
        "english": [
            # Skill demand indicators
            "in-demand", "hot skills", "trending skills", "emerging skills",
            "high demand", "most wanted", "top skills", "must-have skills",
            # Technology-specific skills
            "ai skills", "ml skills", "cloud skills", "devops skills",
            "security skills", "data skills", "programming skills",
            # Skill-related terms
            "skill gap", "skill shortage", "upskilling", "reskilling",
            "skill requirements", "skill demand", "skill trend",
            "programming languages", "frameworks", "libraries",
            # Certifications and qualifications
            "certification in demand", "certification trend",
            # Experience levels
            "senior skills", "junior skills", "mid-level skills",
            # Specialized skills
            "specialized skills", "niche skills", "advanced skills",
            "technical skills", "soft skills"
        ],
        "korean": [
            # Skill demand indicators
            "필요스킬", "핫스킬", "트렌딩스킬", "부상스킬",
            "수요많은스킬", "필수스킬", "인기스킬",
            # Technology-specific skills
            "ai스킬", "ml스킬", "클라우드스킬", "데브옵스스킬",
            "보안스킬", "데이터스킬", "프로그래밍스킬",
            # Skill-related terms
            "스킬갭", "스킬부족", "업스킬링", "리스킬링",
            "스킬요건", "스킬수요", "스킬트렌드",
            "프로그래밍언어", "프레임워크", "라이브러리",
            # Certifications and qualifications
            "인기자격증", "자격증트렌드",
            # Experience levels
            "시니어스킬", "주니어스킬", "중급스킬",
            # Specialized skills
            "전문스킬", "니치스킬", "고급스킬",
            "기술스킬", "소프트스킬"
        ]
    },

    InsightCategory.COMPANY_NEWS: {
        "english": [
            # Company growth and changes
            "expansion", "growth", "new office", "office opening", "hub",
            "global expansion", "international expansion", "market entry",
            # Financial events
            "funding", "investment", "series a", "series b", "series c",
            "venture capital", "ipo", "public offering", "acquisition", "merger",
            "buyout", "exit", "valuation", "unicorn", "investment round",
            # Company status
            "bankruptcy", "insolvency", "restructuring", "reorganization",
            "downsizing", "rightsizing", "spin-off", "divestiture",
            # Leadership changes
            "ceo", "cto", "cfo", "executive", "leadership change",
            "management change", "board of directors", "appoint",
            # Product launches
            "product launch", "new product", "service launch", "feature release",
            # Strategic partnerships
            "partnership", "collaboration", "joint venture", "strategic alliance"
        ],
        "korean": [
            # Company growth and changes
            "확장", "성장", "신설오피스", "오피스오픈", "허브",
            "글로벌확장", "해외확장", "시장진출",
            # Financial events
            "투자", "시리즈a", "시리즈b", "시리즈c",
            "벤처캐피털", "상장", "공모청약", "인수", "합병",
            "매각", "엑싯", "밸류에이션", "유니콘", "투자라운드",
            # Company status
            "부도", "도산", "구조조정", "재조직",
            "감원", "적정인력", "분사", "자매회사",
            # Leadership changes
            "ceo", "cto", "cfo", "임원", "경영진교체",
            "경영진변경", "이사회", "임명",
            # Product launches
            "제품출시", "신제품", "서비스런칭", "기능릴리즈",
            # Strategic partnerships
            "제휴", "협력", "합작투자", "전략적동맹"
        ]
    },

    InsightCategory.SALARY_BENEFITS: {
        "english": [
            # Salary and compensation
            "salary", "wage", "pay", "compensation", "income", "earnings",
            "annual salary", "monthly salary", "base salary", "hourly wage",
            "bonus", "stock options", "equity", "rsu", "stock grant",
            # Salary trends
            "salary increase", "salary hike", "raise", "pay raise",
            "salary trend", "compensation trend", "wage growth",
            # Benefits
            "benefits", "perks", "insurance", "health insurance", "dental",
            "vision", "401k", "pension", "retirement", "paid time off",
            "vacation", "sick leave", "maternity leave", "paternity leave",
            # Work arrangements
            "remote work", "work from home", "hybrid work", "flexible work",
            "work hours", "overtime", "work-life balance",
            # Industry-specific
            "tech salary", "developer salary", "engineer salary",
            "average salary", "salary range", "salary survey", "pay scale"
        ],
        "korean": [
            # Salary and compensation
            "연봉", "급여", "임금", "보수", "소득", "수입",
            "연간연봉", "월급", "기본급", "시급",
            "보너스", "스톡옵션", "지분", "rsu", "주식보상",
            # Salary trends
            "연봉인상", "임금인상", "상여", "급여인상",
            "연봉트렌드", "보수트렌드", "임금성장",
            # Benefits
            "복지", "혜택", "보험", "건강보험", "치과보험",
            "시력보험", "연금", "퇴직금", "휴가", "병가",
            "출산휴가", "육아휴가",
            # Work arrangements
            "재택근무", "원격근무", "하이브리드근무", "유연근무",
            "근무시간", "시간외근무", "워라밸", "업무균형",
            # Industry-specific
            "기업연봉", "개발자연봉", "엔지니어연봉",
            "평균연봉", "연봉구간", "연봉조사", "임금표"
        ]
    },

    InsightCategory.CAREER_DEVELOPMENT: {
        "english": [
            # Career growth
            "career growth", "career path", "career advancement", "promotion",
            "career development", "professional development", "career progression",
            # Learning and training (generic terms, not bootcamp/course/certification)
            "training", "education", "certification", "certified",
            "workshop", "seminar", "online learning", "mooc",
            # Skills development
            "skill development", "learn", "master", "acquire skills",
            "improve skills", "upgrade skills", "new skills",
            # Mentoring and guidance
            "mentor", "mentorship", "coaching", "guidance", "career coach",
            # Career transitions
            "career change", "career pivot", "career switch", "career shift",
            # Leadership development
            "leadership", "management", "leadership training", "management skills",
            # Networking
            "networking", "professional network", "career network",
            # Career advice
            "career advice", "career tips", "career guidance", "job search",
            # Experience
            "internship", "entry level", "mid-level", "senior level",
            "executive level", "work experience", "years of experience"
        ],
        "korean": [
            # Career growth
            "커리어성장", "커리어패스", "진급", "승진",
            "커리어개발", "전문성개발", "경력진급",
            # Learning and training (generic terms, not bootcamp/course/certification)
            "교육", "훈련", "과정", "자격증", "인증",
            "워크샵", "세미나", "온라인학습", "mooc",
            # Skills development
            "스킬개발", "학습", "마스터", "스킬습득",
            "스킬향상", "스킬업그레이드", "신규스킬",
            # Mentoring and guidance
            "멘토", "멘토링", "코칭", "지도", "커리어코치",
            # Career transitions
            "커리어변경", "커리어전환", "직무변경", "커리어시프트",
            # Leadership development
            "리더십", "매니지먼트", "리더십교육", "관리기술",
            # Networking
            "네트워킹", "프로페셔널네트워크", "커리어네트워크",
            # Career advice
            "커리어조언", "커리어팁", "커리어가이드", "구직",
            # Experience
            "인턴십", "주니어", "미드레벨", "시니어",
            "임원급", "경력", "경력년수"
        ]
    },

    InsightCategory.JOB_OPENINGS: {
        "english": [
            # Job posting indicators
            "hiring for", "recruiting for", "job opening", "job posting",
            "job vacancy", "job listing", "we're hiring", "join our team",
            "careers", "open position", "vacancy", "job opportunity",
            # Specific job roles
            "developer job", "engineer job", "manager job", "analyst job",
            "designer job", "product manager job", "data scientist job",
            "full stack developer", "frontend developer", "backend developer",
            # Application-related
            "apply now", "application", "send resume", "submit cv",
            # Job fair and events
            "job fair", "career fair", "hiring event", "recruitment event",
            "recruitment drive", "hiring blitz",
            # Urgent hiring
            "urgent hiring", "immediate start", "hire immediately",
            "multiple positions", "several openings"
        ],
        "korean": [
            # Job posting indicators
            "채용공고", "구인공고", "채용", "모집",
            "빈자리", "채용사이트", "우리는채용중", "팀에합류",
            "채용정보", "채용포지션", "공석", "채용기회",
            # Specific job roles
            "개발자채용", "엔지니어채용", "매니저채용", "분석가채용",
            "디자이너채용", "pm채용", "데이터사이언티스트채용",
            "풀스택개발자", "프론트엔드개발자", "백엔드개발자",
            # Application-related
            "지원", "입사지원", "이력서제출", "자기소개서제출",
            # Job fair and events
            "채용박람회", "커리어페어", "채용행사", "채용이벤트",
            "대규모채용", "채용캠페인",
            # Urgent hiring
            "긴급채용", "즉시입사", "즉시채용",
            "다수채용", "여러포지션"
        ]
    },

    InsightCategory.INDUSTRY_OUTLOOK: {
        "english": [
            # Industry trends and predictions
            "industry trend", "market trend", "future of", "outlook",
            "forecast", "prediction", "projection", "trend report",
            # Growth and decline
            "growth market", "declining market", "emerging market",
            "mature market", "saturated market", "expanding market",
            # Industry-specific outlooks
            "tech outlook", "ai outlook", "blockchain outlook", "cloud outlook",
            "startup outlook", "job market outlook", "career outlook",
            # Analysis and reports
            "market analysis", "industry analysis", "market research",
            "industry report", "trend analysis", "market intelligence",
            # Future implications
            "future jobs", "future skills", "future of work", "job market 2025",
            "workplace of the future", "technology impact on jobs"
        ],
        "korean": [
            # Industry trends and predictions
            "산업트렌드", "시장트렌드", "미래", "전망",
            "예측", "추정", "전망보고서", "트렌드리포트",
            # Growth and decline
            "성장시장", "쇠퇴시장", "부상시장",
            "성숙시장", "포화시장", "확장시장",
            # Industry-specific outlooks
            "기술전망", "ai전망", "블록체인전망", "클라우드전망",
            "스타트업전망", "채용시장전망", "커리어전망",
            # Analysis and reports
            "시장분석", "산업분석", "시장조사",
            "산업리포트", "트렌드분석", "마켓인텔리전스",
            # Future implications
            "미래직업", "미래스킬", "미래노동", "2025년채용시장",
            "미래직장", "기술직업영향"
        ]
    },

    InsightCategory.TECH_UPDATES: {
        "english": [
            # New technologies
            "new technology", "emerging technology", "latest tech",
            "tech breakthrough", "innovation", "disruptive technology",
            # Framework and tool updates
            "new framework", "framework update", "new version", "release",
            "library update", "tool update", "version update",
            # Technology adoption
            "adoption", "implementation", "deployment", "integration",
            # Technology impact on jobs
            "automation", "ai impact", "job displacement", "job creation",
            "skill obsolescence", "obsolete skills", "future skills",
            # Industry-specific tech
            "ai tools", "ml tools", "devops tools", "cloud services",
            "security tools", "data tools", "development tools"
        ],
        "korean": [
            # New technologies
            "신기술", "부상기술", "최신기술",
            "기술혁신", "파괴적혁신", "기술돌파구",
            # Framework and tool updates
            "새프레임워크", "프레임워크업데이트", "신버전", "릴리즈",
            "라이브러리업데이트", "툴업데이트", "버전업데이트",
            # Technology adoption
            "도입", "구현", "배포", "통합",
            # Technology impact on jobs
            "자동화", "ai영향", "일자리대체", "일자리창출",
            "스킬폐기", "구식스킬", "미래스킬",
            # Industry-specific tech
            "ai툴", "ml툴", "데브옵스툴", "클라우드서비스",
            "보안툴", "데이터툴", "개발툴"
        ]
    },

    InsightCategory.WORKPLACE_CULTURE: {
        "english": [
            # Culture aspects
            "company culture", "workplace culture", "organizational culture",
            "team culture", "work environment", "office culture",
            # Work-life balance
            "work-life balance", "flexible hours", "flex schedule",
            "four day work week", "compressed work week",
            # Diversity and inclusion
            "diversity", "inclusion", "dei", "equal opportunity",
            "gender equality", "diverse team", "inclusive workplace",
            # Employee wellbeing
            "employee wellbeing", "mental health", "stress management",
            "burnout prevention", "employee satisfaction",
            # Team dynamics
            "team building", "collaboration", "teamwork",
            "remote culture", "distributed team",
            # Policies
            "remote policy", "hybrid policy", "work from anywhere",
            "return to office", "rto", "office policy"
        ],
        "korean": [
            # Culture aspects
            "회사문화", "직장문화", "조직문화",
            "팀문화", "업무환경", "오피스문화",
            # Work-life balance
            "워라밸", "유연근무제", "탄력근무",
            "주4일제", "단축근무",
            # Diversity and inclusion
            "다양성", "포용성", "dei", "기회균등",
            "성평등", "다양한팀", "포용적직장",
            # Employee wellbeing
            "직원웰빙", "정신건강", "스트레스관리",
            "번아웃예방", "직원만족",
            # Team dynamics
            "팀빌딩", "협업", "팀워크",
            "원격문화", "분산팀",
            # Policies
            "재택근무정책", "하이브리드정책", "어디서든근무",
            "사무실복귀", "rto", "사무실정책"
        ]
    },

    InsightCategory.EDUCATION_TRAINING: {
        "english": [
            # Learning programs
            "bootcamp", "coding bootcamp", "tech bootcamp",
            "online course", "coursera", "udemy", "edX", "pluralsight",
            "training program", "certification program", "certificate course",
            # Educational resources
            "tutorial", "guide", "documentation", "learning path",
            "curriculum", "syllabus", "course material",
            # Skills training
            "python course", "javascript course", "java course",
            "cloud training", "devops training", "security training",
            "data science course", "ml course", "ai course",
            # Professional development
            "professional development", "continuing education", "upskilling",
            "reskilling", "skill training", "career training",
            # Scholarships and funding
            "scholarship", "funding", "grant", "tuition reimbursement",
            # Industry certifications
            "aws certification", "azure certification", "gcp certification",
            "pmp certification", "cissp certification", "agile certification"
        ],
        "korean": [
            # Learning programs
            "부트캠프", "코딩부트캠프", "테크부트캠프",
            "온라인강의", "코세라", "유데미", "edx", "플럴럴사이트",
            "교육프로그램", "자격증프로그램", "자격증코스",
            # Educational resources
            "튜토리얼", "가이드", "문서", "학습경로",
            "커리큘럼", "실라버스", "강의자료",
            # Skills training
            "파이썬강의", "자바스크립트강의", "자바강의",
            "클라우드교육", "데브옵스교육", "보안교육",
            "데이터사이언스강의", "ml강의", "ai강의",
            # Professional development
            "전문개발", "평생교육", "업스킬링",
            "리스킬링", "스킬교육", "커리어교육",
            # Scholarships and funding
            "장학금", "자금지원", "보조금", "수료료지원",
            # Industry certifications
            "aws자격증", "azure자격증", "gcp자격증",
            "pmp자격증", "cissp자격증", "애자일자격증"
        ]
    }
}


def classify_insight(
    url: str,
    title: str,
    content: Optional[str] = None
) -> InsightCategory:
    """Classify an article's insight category for job seekers.

    This function analyzes articles to determine what type of insight
    they provide for job seekers, focusing on relevance rather than
    technical topic.

    Args:
        url: Article URL
        title: Article title
        content: Optional article content for additional context

    Returns:
        Detected insight category (defaults to InsightCategory.OTHER if no match)
    """
    url_lower = url.lower()
    title_lower = title.lower()
    content_lower = content.lower() if content else ""

    # Combine searchable text
    searchable_text = f"{url_lower} {title_lower} {content_lower}"

    # Define priority order for categories (more specific categories first)
    category_priority = [
        InsightCategory.JOB_OPENINGS,
        InsightCategory.SALARY_BENEFITS,
        InsightCategory.IN_DEMAND_SKILLS,
        InsightCategory.HIRING_TRENDS,
        InsightCategory.COMPANY_NEWS,
        InsightCategory.CAREER_DEVELOPMENT,
        InsightCategory.INDUSTRY_OUTLOOK,
        InsightCategory.WORKPLACE_CULTURE,
        InsightCategory.TECH_UPDATES,
        InsightCategory.EDUCATION_TRAINING,
    ]

    # Check each category's keywords in priority order
    for category in category_priority:
        keywords_dict = INSIGHT_KEYWORDS.get(category, {})

        # Check English keywords
        for keyword in keywords_dict.get("english", []):
            if _contains_keyword(keyword, searchable_text):
                logger.debug(
                    f"Classified insight as {category}: "
                    f"matched English keyword '{keyword}'"
                )
                return category

        # Check Korean keywords
        for keyword in keywords_dict.get("korean", []):
            if _contains_keyword(keyword, searchable_text):
                logger.debug(
                    f"Classified insight as {category}: "
                    f"matched Korean keyword '{keyword}'"
                )
                return category

    # Default to OTHER if no category matches
    logger.debug("No insight category match, defaulting to OTHER")
    return InsightCategory.OTHER


def _contains_keyword(keyword: str, text: str) -> bool:
    """Check if a keyword appears in text with proper word boundary matching.

    Args:
        keyword: Keyword to search for
        text: Text to search in

    Returns:
        True if keyword is found, False otherwise
    """
    # For multi-word keywords, check exact phrase match (case-insensitive)
    if " " in keyword:
        return keyword.lower() in text.lower()

    # For single-word keywords, check word boundary matching (case-insensitive)
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return re.search(pattern, text, re.IGNORECASE) is not None


def get_insight_keywords(category: InsightCategory) -> dict[str, list[str]]:
    """Get all keywords associated with an insight category.

    Args:
        category: Insight category enum value

    Returns:
        Dictionary with "english" and "korean" keyword lists
    """
    if category in INSIGHT_KEYWORDS:
        return INSIGHT_KEYWORDS[category]
    return {"english": [], "korean": []}


def get_insight_description(category: InsightCategory) -> str:
    """Get a human-readable description for an insight category.

    Args:
        category: Insight category enum value

    Returns:
        Category description string
    """
    descriptions = {
        InsightCategory.HIRING_TRENDS: (
            "Hiring trends, recruitment patterns, and job market movements"
        ),
        InsightCategory.IN_DEMAND_SKILLS: (
            "Skills currently in high demand and emerging skill trends"
        ),
        InsightCategory.COMPANY_NEWS: (
            "Company expansions, funding, acquisitions, and strategic changes"
        ),
        InsightCategory.SALARY_BENEFITS: (
            "Salary trends, compensation packages, benefits, and work arrangements"
        ),
        InsightCategory.CAREER_DEVELOPMENT: (
            "Career growth opportunities, training, and professional development"
        ),
        InsightCategory.JOB_OPENINGS: (
            "Specific job postings and immediate hiring opportunities"
        ),
        InsightCategory.INDUSTRY_OUTLOOK: (
            "Industry predictions, market trends, and future outlook"
        ),
        InsightCategory.TECH_UPDATES: (
            "New technologies and their impact on job requirements"
        ),
        InsightCategory.WORKPLACE_CULTURE: (
            "Company culture, work-life balance, and workplace policies"
        ),
        InsightCategory.EDUCATION_TRAINING: (
            "Educational resources, courses, and training programs"
        ),
        InsightCategory.OTHER: (
            "Other topics not specifically relevant to job seekers"
        )
    }
    return descriptions.get(category, "Unknown Category")


def get_insight_priority(category: InsightCategory) -> int:
    """Get priority level for insight category (lower = higher priority).

    Higher priority insights are more directly actionable for job seekers.

    Args:
        category: Insight category enum value

    Returns:
        Priority level (0-9, where 0 is highest priority)
    """
    priorities = {
        InsightCategory.JOB_OPENINGS: 0,          # Most actionable
        InsightCategory.SALARY_BENEFITS: 1,       # Direct financial impact
        InsightCategory.IN_DEMAND_SKILLS: 2,      # Immediate skill relevance
        InsightCategory.HIRING_TRENDS: 3,        # Market intelligence
        InsightCategory.COMPANY_NEWS: 4,          # Company-specific info
        InsightCategory.CAREER_DEVELOPMENT: 5,    # Long-term planning
        InsightCategory.INDUSTRY_OUTLOOK: 6,      # Strategic insights
        InsightCategory.WORKPLACE_CULTURE: 7,     # Cultural fit info
        InsightCategory.TECH_UPDATES: 8,          # Future relevance
        InsightCategory.EDUCATION_TRAINING: 9,     # Learning resources
        InsightCategory.OTHER: 10,                 # Lowest priority
    }
    return priorities.get(category, 10)


def get_all_insight_categories() -> list[InsightCategory]:
    """Get all available insight categories.

    Returns:
        List of all insight categories
    """
    return [
        InsightCategory.HIRING_TRENDS,
        InsightCategory.IN_DEMAND_SKILLS,
        InsightCategory.COMPANY_NEWS,
        InsightCategory.SALARY_BENEFITS,
        InsightCategory.CAREER_DEVELOPMENT,
        InsightCategory.JOB_OPENINGS,
        InsightCategory.INDUSTRY_OUTLOOK,
        InsightCategory.TECH_UPDATES,
        InsightCategory.WORKPLACE_CULTURE,
        InsightCategory.EDUCATION_TRAINING,
        InsightCategory.OTHER,
    ]


# Export public API
__all__ = [
    "InsightCategory",
    "classify_insight",
    "get_insight_keywords",
    "get_insight_description",
    "get_insight_priority",
    "get_all_insight_categories",
    "INSIGHT_KEYWORDS",
]
