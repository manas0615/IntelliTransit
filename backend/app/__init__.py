"""
IntelliTransit Flask Application Factory.
"""
import os
import logging
from pathlib import Path
from flask import Flask, send_from_directory, send_file
from backend.app.config import get_config
from backend.app.models.db import init_db_pool, close_db_pool
from backend.app.middleware import (
    register_error_handlers,
    register_request_logging,
    register_cors,
    register_rate_limiter
)

logger = logging.getLogger(__name__)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory constructing a configured Flask app instance.
    """
    config_class = get_config(config_name)

    frontend_path = config_class.FRONTEND_DIR
    app = Flask(
        __name__,
        static_folder=str(frontend_path),
        static_url_path=""
    )
    app.config.from_object(config_class)

    # Initialize Logging
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    )

    # Initialize Database Connection Pool (if not in testing or if DB configured)
    try:
        init_db_pool(
            database_url=app.config["DATABASE_URL"],
            minconn=app.config["DB_POOL_MIN_CONN"],
            maxconn=app.config["DB_POOL_MAX_CONN"]
        )
    except Exception as e:
        logger.warning("Could not pre-initialize DB pool in app factory (will retry on query): %s", e)

    # Register Middlewares
    register_cors(app)
    register_request_logging(app)
    register_rate_limiter(app)
    register_error_handlers(app)

    # Register Core API Blueprints
    from backend.app.routes.health import health_bp
    app.register_blueprint(health_bp)

    # Register Domain Blueprints (imported conditionally/as built)
    try:
        from backend.app.routes.auth import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.users import users_bp
        app.register_blueprint(users_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.locations import locations_bp
        app.register_blueprint(locations_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.journeys import journeys_bp
        app.register_blueprint(journeys_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.tickets import tickets_bp
        app.register_blueprint(tickets_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.passes import passes_bp
        app.register_blueprint(passes_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.payments import payments_bp
        app.register_blueprint(payments_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.validation import validation_bp
        app.register_blueprint(validation_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.ai import ai_bp
        app.register_blueprint(ai_bp)
    except ImportError:
        pass

    try:
        from backend.app.routes.admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        pass

    # Static Frontend MPA File Serving
    @app.route("/", methods=["GET"])
    def serve_index():
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return send_file(index_file)
        return {"message": "IntelliTransit API active. Frontend index.html not yet built."}, 200

    @app.route("/<path:path>", methods=["GET"])
    def serve_static(path):
        # Don't intercept API routes
        if path.startswith("api/"):
            from flask import abort
            abort(404)
        target_file = frontend_path / path
        if target_file.exists() and target_file.is_file():
            return send_file(target_file)
        # If accessing a page like /planner or /planner.html
        if not path.endswith(".html"):
            html_file = frontend_path / f"{path}.html"
            if html_file.exists():
                return send_file(html_file)
        from flask import abort
        abort(404)

    return app
