"""
IntelliTransit - Payment Routes
Endpoints for simulated demo payment order initialization, confirmation, and payment history.
Real payment gateway integration is outside the scope of this academic demonstration.
"""

from flask import Blueprint, request, g
from backend.app.services.payment_service import PaymentService
from backend.app.middleware.auth_middleware import require_auth
from backend.app.utils.validators import parse_pagination
from backend.app.utils.responses import success_response, error_response

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payments_bp.route('/create-order', methods=['POST'])
@payments_bp.route('/create', methods=['POST'])
@require_auth
def create_order():
    """
    Initialize a simulated payment session for ticket or pass.
    Body:
      {
        "item_type": "TICKET" | "PASS",
        "item_id": "uuid"
      }
    """
    user = getattr(g, "current_user", None)
    data = request.get_json(silent=True) or {}

    item_type = data.get('item_type') or data.get('entity_type')
    item_id = data.get('item_id') or data.get('entity_id')

    if not item_type or not item_id:
        return error_response('VALIDATION_ERROR', 'item_type and item_id are required', status_code=400)

    success, result, message = PaymentService.create_order_for_item(
        user_id=user["user_id"],
        item_type=item_type,
        item_id=item_id
    )

    if not success:
        return error_response(result.get("code", "ORDER_CREATION_FAILED"), message, status_code=400)

    return success_response(result, message=message, status_code=201)


@payments_bp.route('/confirm', methods=['POST'])
@payments_bp.route('/simulate', methods=['POST'])
@payments_bp.route('/verify', methods=['POST'])
@require_auth
def confirm_payment():
    """
    Confirm simulated demo payment and atomically activate ticket or pass.
    Body:
      {
        "payment_id": "uuid",
        "transaction_reference": "DEMO-..." (optional)
      }
    """
    user = getattr(g, "current_user", None)
    data = request.get_json(silent=True) or {}

    payment_id = data.get('payment_id')
    tx_ref = data.get('transaction_reference') or data.get('order_reference') or data.get('order_id')

    if not payment_id and not tx_ref:
        return error_response(
            'VALIDATION_ERROR',
            'payment_id or transaction_reference is required to confirm payment',
            status_code=400
        )

    success, result, message = PaymentService.confirm_simulated_payment(
        user_id=user["user_id"],
        payment_id=payment_id,
        transaction_reference=tx_ref
    )

    if not success:
        code = result.get("code", "PAYMENT_CONFIRMATION_FAILED")
        status_code = 400
        if code in ("FORBIDDEN", "UNAUTHORIZED"):
            status_code = 403
        elif code in ("PAYMENT_NOT_FOUND", "NOT_FOUND"):
            status_code = 404
        return error_response(code, message, status_code=status_code, details=result)

    return success_response(result, message=message, status_code=200)


@payments_bp.route('', methods=['GET'])
@payments_bp.route('/history', methods=['GET'])
@require_auth
def get_payment_history():
    """Get simulated payment history for the authenticated user."""
    user = getattr(g, "current_user", None)
    limit, offset = parse_pagination(request.args.get('limit'), request.args.get('offset'))

    try:
        payments = PaymentService.list_user_payments(user["user_id"], limit=limit, offset=offset)
        return success_response({
            'payments': payments,
            'count': len(payments),
            'limit': limit,
            'offset': offset
        }, message="Payments loaded.")
    except Exception as e:
        return error_response('INTERNAL_SERVER_ERROR', str(e), status_code=500)


@payments_bp.route('/<payment_id>', methods=['GET'])
@require_auth
def get_payment_details(payment_id):
    """Get details for a specific payment."""
    user = getattr(g, "current_user", None)
    payment = PaymentService.get_payment_details(payment_id, user_id=user["user_id"])
    if not payment:
        return error_response('NOT_FOUND', 'Payment not found or unauthorized', status_code=404)
    return success_response(payment, message="Payment details loaded.")
