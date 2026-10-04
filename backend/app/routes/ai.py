"""
AI Assistant Routes.
Endpoints for conversing with Gemini 2.5 Flash / IntelliTransit Assistant.
"""
from flask import Blueprint, request, g
from backend.app.services.ai_service import AIService
from backend.app.services.ai_tools import GEMINI_TOOLS_DECLARATION
from backend.app.middleware.auth_middleware import optional_auth
from backend.app.utils.responses import success_response, error_response

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/chat", methods=["POST"])
@optional_auth
def chat():
    """
    Chat endpoint for conversational journey planning and transit queries.
    Body:
      {
        "message": "Plan route from Swargate to Pune Station",
        "history": [{"role": "user", "content": "..."}, {"role": "model", "content": "..."}] (optional)
      }
    """
    user = getattr(g, "current_user", None)
    user_id = user["user_id"] if user else None

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return error_response("VALIDATION_ERROR", "Message cannot be empty.", 400)

    try:
        service = AIService(user_id=user_id)
        result = service.chat(message=message, history=history)
        return success_response(data=result, message="AI response generated successfully.")
    except Exception as e:
        return error_response("AI_SERVICE_ERROR", f"Error generating assistant response: {str(e)}", 500)


@ai_bp.route("/tools", methods=["GET"])
def get_tools():
    """Return available function calling tool declarations."""
    return success_response(data={"tools": GEMINI_TOOLS_DECLARATION}, message="AI tools list.")
