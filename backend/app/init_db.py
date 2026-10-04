"""
Database initialization script for IntelliTransit.
Executes schema.sql and seed.sql against PostgreSQL database.
"""
import os
import sys
import logging
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from backend.app.config import get_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def create_database_if_not_exists(database_url: str) -> None:
    """Create the target database if it does not already exist."""
    # Parse DSN or connect to default 'postgres' database
    conn_params = psycopg2.extensions.parse_dsn(database_url)
    target_db = conn_params.pop("dbname", "intellitransit")
    
    # Connect to default 'postgres' maintenance DB
    maintenance_params = conn_params.copy()
    maintenance_params["dbname"] = "postgres"
    
    try:
        conn = psycopg2.connect(**maintenance_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
            exists = cursor.fetchone()
            if not exists:
                logger.info("Database '%s' does not exist. Creating it...", target_db)
                cursor.execute(f'CREATE DATABASE "{target_db}";')
                logger.info("Database '%s' created successfully.", target_db)
            else:
                logger.info("Database '%s' already exists.", target_db)
        conn.close()
    except Exception as e:
        logger.warning("Could not auto-create database (might already exist or restricted): %s", e)


def run_sql_file(database_url: str, sql_file_path: Path) -> None:
    """Execute a complete SQL script file against the target database."""
    if not sql_file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")
    
    logger.info("Executing SQL file: %s", sql_file_path.name)
    sql_content = sql_file_path.read_text(encoding="utf-8")
    
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_content)
        conn.commit()
        logger.info("Successfully executed: %s", sql_file_path.name)
    except Exception as e:
        conn.rollback()
        logger.error("Failed executing %s: %s", sql_file_path.name, e)
        raise
    finally:
        conn.close()


def setup_database(config_name: str = "development") -> bool:
    """Run full schema and seed migration."""
    config = get_config(config_name)
    db_url = config.DATABASE_URL
    logger.info("Setting up database for configuration '%s' at: %s", config_name, db_url)
    
    try:
        create_database_if_not_exists(db_url)
        run_sql_file(db_url, BASE_DIR / "database" / "schema.sql")
        run_sql_file(db_url, BASE_DIR / "database" / "seed.sql")
        logger.info("Database setup completed successfully.")
        return True
    except Exception as e:
        logger.error("Database setup failed: %s", e)
        return False


if __name__ == "__main__":
    cfg = sys.argv[1] if len(sys.argv) > 1 else "development"
    success = setup_database(cfg)
    sys.exit(0 if success else 1)
