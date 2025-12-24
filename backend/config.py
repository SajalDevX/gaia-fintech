"""
GAIA Configuration Module
Global AI-powered Impact Assessment System
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "GAIA - Global AI-powered Impact Assessment"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # AI/ML Configuration (Multi-Provider LLM Support)
    OPENAI_API_KEY: Optional[str] = None  # GPT-4o
    ANTHROPIC_API_KEY: Optional[str] = None  # Claude Haiku
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Google Gemini Configuration
    GOOGLE_GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"  # Fast, experimental model
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"  # Better quality for complex reasoning/debate
    GEMINI_REQUESTS_PER_MINUTE: int = 60
    GEMINI_MAX_RETRIES: int = 3
    GEMINI_RETRY_DELAY: float = 1.0
    GEMINI_CACHE_TTL: int = 3600  # 1 hour cache

    # External Data APIs
    NEWS_API_KEY: Optional[str] = None  # newsapi.org
    ALPHA_VANTAGE_API_KEY: Optional[str] = None  # Financial data
    SEC_EDGAR_USER_AGENT: str = "GAIA ESG Analysis (contact@example.com)"  # Required by SEC

    # Database
    DATABASE_URL: str = "sqlite:///./gaia.db"
    REDIS_URL: str = "redis://localhost:6379"

    # External APIs (Satellite Data)
    NASA_EARTHDATA_API_KEY: Optional[str] = None
    ESA_COPERNICUS_API_KEY: Optional[str] = None

    # Blockchain Configuration
    BLOCKCHAIN_ENABLED: bool = True
    BLOCKCHAIN_NETWORK: str = "testnet"

    # Agent Configuration
    AGENT_TIMEOUT_SECONDS: int = 60
    MAX_CONCURRENT_AGENTS: int = 10
    ADVERSARIAL_DEBATE_ROUNDS: int = 3

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# SDG Configuration
SDG_GOALS = {
    1: {"name": "No Poverty", "icon": "poverty", "color": "#E5243B"},
    2: {"name": "Zero Hunger", "icon": "hunger", "color": "#DDA63A"},
    3: {"name": "Good Health and Well-being", "icon": "health", "color": "#4C9F38"},
    4: {"name": "Quality Education", "icon": "education", "color": "#C5192D"},
    5: {"name": "Gender Equality", "icon": "gender", "color": "#FF3A21"},
    6: {"name": "Clean Water and Sanitation", "icon": "water", "color": "#26BDE2"},
    7: {"name": "Affordable and Clean Energy", "icon": "energy", "color": "#FCC30B"},
    8: {"name": "Decent Work and Economic Growth", "icon": "work", "color": "#A21942"},
    9: {"name": "Industry, Innovation and Infrastructure", "icon": "industry", "color": "#FD6925"},
    10: {"name": "Reduced Inequalities", "icon": "equality", "color": "#DD1367"},
    11: {"name": "Sustainable Cities and Communities", "icon": "cities", "color": "#FD9D24"},
    12: {"name": "Responsible Consumption and Production", "icon": "consumption", "color": "#BF8B2E"},
    13: {"name": "Climate Action", "icon": "climate", "color": "#3F7E44"},
    14: {"name": "Life Below Water", "icon": "water_life", "color": "#0A97D9"},
    15: {"name": "Life on Land", "icon": "land_life", "color": "#56C02B"},
    16: {"name": "Peace, Justice and Strong Institutions", "icon": "peace", "color": "#00689D"},
    17: {"name": "Partnerships for the Goals", "icon": "partnership", "color": "#19486A"},
}

# ESG Categories
ESG_CATEGORIES = {
    "E": {
        "name": "Environmental",
        "factors": [
            "carbon_emissions",
            "energy_efficiency",
            "water_management",
            "waste_management",
            "biodiversity",
            "pollution_control",
            "renewable_energy",
            "deforestation"
        ]
    },
    "S": {
        "name": "Social",
        "factors": [
            "labor_practices",
            "human_rights",
            "community_relations",
            "health_safety",
            "diversity_inclusion",
            "supply_chain_labor",
            "data_privacy",
            "product_safety"
        ]
    },
    "G": {
        "name": "Governance",
        "factors": [
            "board_structure",
            "executive_compensation",
            "shareholder_rights",
            "business_ethics",
            "transparency",
            "anti_corruption",
            "risk_management",
            "regulatory_compliance"
        ]
    }
}

# Risk Levels
RISK_LEVELS = {
    "CRITICAL": {"score_range": (0, 20), "color": "#DC2626", "action": "AVOID"},
    "HIGH": {"score_range": (20, 40), "color": "#EA580C", "action": "CAUTION"},
    "MODERATE": {"score_range": (40, 60), "color": "#CA8A04", "action": "MONITOR"},
    "LOW": {"score_range": (60, 80), "color": "#16A34A", "action": "ACCEPTABLE"},
    "MINIMAL": {"score_range": (80, 100), "color": "#059669", "action": "RECOMMENDED"}
}
