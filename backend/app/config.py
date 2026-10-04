"""
IntelliTransit Application Configuration Module.
Provides environment-aware configuration classes with strict type handling and defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base Configuration with common settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "intellitransit-default-secret-key-change-me")
    
    # PostgreSQL Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:admin@localhost:5432/intellitransit"
    )
    DB_POOL_MIN_CONN = int(os.getenv("DB_POOL_MIN_CONN", "1"))
    DB_POOL_MAX_CONN = int(os.getenv("DB_POOL_MAX_CONN", "20"))
    
    # JWT Authentication
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "intellitransit-jwt-secret-key-super-secure-change-in-prod-256bit"
    )
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "24"))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    
    # OpenTripPlanner 2
    OTP_BASE_URL = os.getenv("OTP_BASE_URL", "http://localhost:8080").rstrip("/")
    OTP_ROUTER_ID = os.getenv("OTP_ROUTER_ID", "default")
    OTP_TIMEOUT_SECONDS = int(os.getenv("OTP_TIMEOUT_SECONDS", "10"))
    
    # Gemini AI (Optional - Local demo fallback used when key is absent)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Pune Metropolitan Bounding Box
    PUNE_BOUNDS_MIN_LAT = float(os.getenv("PUNE_BOUNDS_MIN_LAT", "18.35"))
    PUNE_BOUNDS_MAX_LAT = float(os.getenv("PUNE_BOUNDS_MAX_LAT", "18.70"))
    PUNE_BOUNDS_MIN_LNG = float(os.getenv("PUNE_BOUNDS_MIN_LNG", "73.65"))
    PUNE_BOUNDS_MAX_LNG = float(os.getenv("PUNE_BOUNDS_MAX_LNG", "74.05"))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Static & Template paths
    FRONTEND_DIR = BASE_DIR / "frontend"
    STATIC_DIR = BASE_DIR / "frontend"
    
    TESTING = False
    DEBUG = False


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:admin@localhost:5432/intellitransit_test"
    )
    DB_POOL_MIN_CONN = 1
    DB_POOL_MAX_CONN = 5
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = 1
    RATE_LIMIT_PER_MINUTE = 1000


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


def get_config(config_name=None):
    """Return the active configuration object."""
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(config_name, DevelopmentConfig)
