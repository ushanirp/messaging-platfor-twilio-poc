from flask import Blueprint, request, jsonify
from app.services.webhook_service import WebhookService

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route("/webhooks/twilio/inbound", methods=["POST"])
def twilio_inbound():
    """Handle inbound Twilio webhooks"""
    if not WebhookService.validate_twilio_signature():
        return "", 403
    
    data = request.form.to_dict()
    WebhookService.handle_inbound_webhook(data)
    return "", 204

@webhooks_bp.route("/webhooks/twilio/status", methods=["POST"])
def twilio_status():
    """Handle Twilio status webhooks"""
    if not WebhookService.validate_twilio_signature():
        return "", 403
    
    data = request.form.to_dict()
    WebhookService.handle_status_webhook(data)
    return "", 204