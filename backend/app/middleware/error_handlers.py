"""
Global HTTP error handlers for IntelliTransit Flask backend.
Translates HTTP errors and uncaught exceptions into standard JSON error responses.
"""
import logging
from flask import Flask
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from backend.app.utils.responses import error_response

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """Register all global error handlers onto the Flask application instance."""

    @app.errorhandler(400)
    def bad_request(e):
        return error_response("BAD_REQUEST", str(e.description) if hasattr(e, "description") else "Bad request.", 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error_response("UNAUTHORIZED", str(e.description) if hasattr(e, "description") else "Authentication required.", 401)

    @app.errorhandler(403)
    def forbidden(e):
        return error_response("FORBIDDEN", str(e.description) if hasattr(e, "description") else "You do not have permission to access this resource.", 403)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("NOT_FOUND", str(e.description) if hasattr(e, "description") else "The requested resource was not found.", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("METHOD_NOT_ALLOWED", "The HTTP method is not allowed for this endpoint.", 405)

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return error_response("UNPROCESSABLE_ENTITY", "Unable to process the request payload.", 422)

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return error_response("RATE_LIMIT_EXCEEDED", "Too many requests. Please slow down and try again later.", 429)

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(e: ValidationError):
        return error_response("VALIDATION_ERROR", "Invalid input data provided.", 400, details=e.messages)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        code = e.code or 500
        err_name = getattr(e, "name", "HTTP_ERROR").upper().replace(" ", "_")
        return error_response(err_name, e.description, code)

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        logger.exception("Unhandled server exception: %s", e)
        # Production security: never leak internal stack traces
        return error_response("INTERNAL_SERVER_ERROR", "An unexpected server error occurred. Please try again later.", 500)
