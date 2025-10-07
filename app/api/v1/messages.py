from flask import Blueprint, request, jsonify, current_app
from app.models.message import Message
from app.services.messaging_service import MessagingService
from app.utils.phone_utils import normalize_phone, validate_e164

messages_bp = Blueprint('messages', __name__)

@messages_bp.route("/messages", methods=["GET"])
def list_messages():
    """Get messages with optional campaign filter"""
    campaign_id = request.args.get('campaign_id')
    
    if campaign_id:
        messages = Message.get_by_campaign(campaign_id)
    else:
        messages = Message.get_all()
    
    return jsonify([message.to_dict() for message in messages])

@messages_bp.route("/test/send", methods=["POST"])
def test_send_message():
    """Test endpoint to send a WhatsApp message directly"""
    data = request.json or {}
    phone = data.get('phone')
    message_text = data.get('message')
    
    if not phone or not message_text:
        return jsonify({"error": "phone and message are required"}), 400
    
    try:
        phone_normalized = normalize_phone(phone)
        if not validate_e164(phone_normalized):
            return jsonify({"error": "invalid phone number"}), 400
        
        message_sid = MessagingService.send_whatsapp_message(phone_normalized, message_text)
        return jsonify({"success": True, "message_sid": message_sid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@messages_bp.route("/test/send/verified", methods=["POST"])
def test_send_verified():
    """Test sending to verified numbers only"""
    data = request.json or {}
    phone = data.get('phone')
    message_text = data.get('message')
    
    if not phone or not message_text:
        return jsonify({"error": "phone and message are required"}), 400
    
    try:
        verified_numbers = current_app.config.get('VERIFIED_NUMBERS', [])
        
        phone_normalized = normalize_phone(phone)
        
        # Check if number is verified (for trial accounts)
        if verified_numbers and not any(phone_normalized.endswith(num.replace('+', '')) for num in verified_numbers):
            return jsonify({
                "error": "Number not verified. Trial accounts can only send to verified numbers.",
                "verified_numbers": verified_numbers
            }), 400
        
        message_sid = MessagingService.send_whatsapp_message(phone_normalized, message_text)
        return jsonify({"success": True, "message_sid": message_sid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500