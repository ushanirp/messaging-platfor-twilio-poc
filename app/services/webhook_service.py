import json
from twilio.request_validator import RequestValidator
from flask import request, current_app
from app.models.user import User
from app.models.event import InboundEvent, DeliveryReceipt
from app.models.message import Message

class WebhookService:
    @staticmethod
    def validate_twilio_signature():
        '''Validate Twilio webhook signature'''
        if not current_app.config.get('TWILIO_VALIDATE_WEBHOOKS', False):
            return True
        
        validator = WebhookService._get_twilio_validator()
        if not validator:
            return True
        
        url = request.url
        signature = request.headers.get('X-Twilio-Signature', '')
        return validator.validate(url, request.form, signature)
    
    @staticmethod
    def _get_twilio_validator():
        '''Get Twilio request validator'''
        token = current_app.config.get('TWILIO_AUTH_TOKEN')
        if not token:
            return None
        return RequestValidator(token)
    
    @staticmethod
    def handle_inbound_webhook(data):
        '''Handle inbound message webhook'''
        incoming_from = data.get('From')
        incoming_to = data.get('To')
        body = data.get('Body')
        
        # Save inbound event
        event = InboundEvent(
            raw_payload=data,
            from_number=incoming_from,
            body=body,
            message_sid=data.get('MessageSid'),
            timestamp=data.get('Timestamp')
        )
        event.save()
        
        # Handle opt-out
        if body and body.strip().lower() in ('stop', 'unsubscribe'):
            WebhookService._handle_opt_out(incoming_from)
        
        return event
    
    @staticmethod
    def _handle_opt_out(phone):
        '''Handle user opt-out'''
        phone_clean = phone.replace('whatsapp:', '') if phone else phone
        if phone_clean:
            user = User.get_by_phone(phone_clean)
            if user:
                # Update consent state directly
                user.consent_state = 'OPT_OUT'
                User.create_or_update(user.phone_number, user.attributes, {'whatsapp': False})
    
    @staticmethod
    def handle_status_webhook(data):
        '''Handle message status webhook'''
        sid = data.get('MessageSid') or data.get('SmsSid')
        status = data.get('MessageStatus') or data.get('Status')
        
        # Find message by provider_message_sid
        message = None
        if sid:
            from app.database.connection import get_db
            db = get_db()
            row = db.execute(
                "SELECT * FROM messages WHERE provider_message_sid=?", 
                (sid,)
            ).fetchone()
            if row:
                message = Message._row_to_message(row)
        
        # Update message status
        if message:
            # Convert Twilio status to our state
            status_map = {
                'queued': 'QUEUED',
                'sending': 'SENDING', 
                'sent': 'SENT',
                'delivered': 'DELIVERED',
                'read': 'READ',
                'failed': 'FAILED',
                'undelivered': 'UNDLVD'
            }
            message.state = status_map.get(status, 'FAILED')
            message.save()
        
        # Save delivery receipt
        receipt = DeliveryReceipt(
            raw_payload=data,
            message_sid=sid,
            message_status=status,
            error_code=data.get('ErrorCode'),
            timestamp=data.get('Timestamp')
        )
        receipt.save()
        
        return receipt