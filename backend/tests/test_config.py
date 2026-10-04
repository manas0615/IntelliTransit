"""
Unit tests for configuration loading and environment defaults.
"""
from backend.app.config import (
    Config,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    get_config,
)


def test_development_config():
    """Verify DevelopmentConfig settings."""
    cfg = get_config("development")
    assert cfg.DEBUG is True
    assert cfg.TESTING is False
    assert cfg.OTP_ROUTER_ID == "default"
    assert "postgresql://" in cfg.DATABASE_URL
    assert cfg.PUNE_BOUNDS_MIN_LAT < cfg.PUNE_BOUNDS_MAX_LAT
    assert cfg.PUNE_BOUNDS_MIN_LNG < cfg.PUNE_BOUNDS_MAX_LNG


def test_testing_config():
    """Verify TestingConfig settings."""
    cfg = get_config("testing")
    assert cfg.TESTING is True
    assert cfg.DEBUG is True
    assert cfg.JWT_ACCESS_TOKEN_EXPIRES_HOURS == 1


def test_production_config():
    """Verify ProductionConfig settings."""
    cfg = get_config("production")
    assert cfg.DEBUG is False
    assert cfg.TESTING is False


def test_pune_bounding_box_constants():
    """Verify Pune geographic boundaries match specifications."""
    cfg = Config
    assert 18.0 <= cfg.PUNE_BOUNDS_MIN_LAT <= 18.5
    assert 18.5 <= cfg.PUNE_BOUNDS_MAX_LAT <= 19.0
    assert 73.0 <= cfg.PUNE_BOUNDS_MIN_LNG <= 73.8
    assert 73.8 <= cfg.PUNE_BOUNDS_MAX_LNG <= 74.5
