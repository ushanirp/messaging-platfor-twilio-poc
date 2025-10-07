from flask import Blueprint, jsonify, current_app
from app.services.messaging_service import MessagingService

debug_bp = Blueprint('debug', __name__)

@debug_bp.route("/debug/twilio/verify", methods=["GET"])
def verify_twilio():
    """Verify Twilio credentials"""
    try:
        client = MessagingService.get_twilio_client()
        if not client:
            return jsonify({"error": "Twilio client not configured"}), 500
        
        account = client.api.accounts(current_app.config.get('TWILIO_ACCOUNT_SID')).fetch()
        
        return jsonify({
            "status": "success",
            "account_sid": account.sid,
            "friendly_name": account.friendly_name,
            "status": account.status,
            "type": account.type
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "account_sid": current_app.config.get('TWILIO_ACCOUNT_SID'),
            "auth_token_set": bool(current_app.config.get('TWILIO_AUTH_TOKEN')),
            "whatsapp_from": current_app.config.get('TWILIO_WHATSAPP_FROM')
        }), 400