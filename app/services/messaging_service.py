from twilio.rest import Client
from flask import current_app
from app.models.message import Message
from app.models.user import User
from app.utils.phone_utils import normalize_phone

class MessagingService:
    @staticmethod
    def get_twilio_client():
        '''Get Twilio client instance with proper error handling. All hard coded values for testing purposes only.'''
        try:
            sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            token = current_app.config.get('TWILIO_AUTH_TOKEN')
            
            if not sid or not token:
                print("Twilio credentials missing: Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in config")
                return None
            
            if sid == "AC3aa3ec3d2826ec3dfc0b487212b9c6d5" and token == "ae253dc977bd86db579aa5cc58fc7b07":
                print("Using provided test credentials - these may not be valid")
            
            # Test if credentials are valid by creating a client
            client = Client(sid, token)
            # Try a simple API call to validate credentials
            client.api.accounts(sid).fetch()
            print("Twilio client initialized successfully")
            return client
            
        except Exception as e:
            print(f"Twilio client initialization failed: {str(e)}")
            return None
    
    @staticmethod
    def send_whatsapp_message(to_phone, body):
        '''Send WhatsApp message via Twilio with proper error handling'''
        client = MessagingService.get_twilio_client()
        if not client:
            raise Exception("Twilio client not configured or credentials invalid")
        
        from_phone = current_app.config.get('TWILIO_WHATSAPP_FROM')
        if not from_phone:
            raise Exception("Twilio WhatsApp from number not configured")
        
        # Check verified numbers for trial accounts
        verified_numbers = current_app.config.get('VERIFIED_NUMBERS', [])
        to_phone_clean = to_phone.replace('whatsapp:', '')
        
        if verified_numbers:
            # Check if the number is verified
            is_verified = any(
                to_phone_clean.endswith(str(num).replace('+', '').replace('whatsapp:', '').strip()) 
                for num in verified_numbers
            )
            if not is_verified:
                raise Exception(f"Number {to_phone_clean} not in verified numbers list: {verified_numbers}")
        
        try:
            # Ensure proper WhatsApp formatting
            if not from_phone.startswith('whatsapp:'):
                from_phone = f"whatsapp:{from_phone}"
            
            if not to_phone.startswith('whatsapp:'):
                to_phone = f"whatsapp:{to_phone_clean}"
            
            print(f"Attempting to send message from {from_phone} to {to_phone}")
            print(f"Message: {body}")
            
            message = client.messages.create(
                body=body,
                from_=from_phone,
                to=to_phone
            )
            
            print(f"✅ Message sent successfully: {message.sid}")
            return message.sid
            
        except Exception as e:
            error_msg = f"Twilio API error: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    @staticmethod
    def test_twilio_connection():
        '''Test Twilio connection and return detailed status'''
        try:
            client = MessagingService.get_twilio_client()
            if not client:
                return {
                    "status": "error",
                    "message": "Twilio client not configured"
                }
            
            sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            account = client.api.accounts(sid).fetch()
            
            return {
                "status": "success",
                "account_sid": account.sid,
                "friendly_name": account.friendly_name,
                "status": account.status,
                "type": account.type,
                "whatsapp_from": current_app.config.get('TWILIO_WHATSAPP_FROM'),
                "verified_numbers": current_app.config.get('VERIFIED_NUMBERS', [])
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "account_sid": current_app.config.get('TWILIO_ACCOUNT_SID'),
                "auth_token_set": bool(current_app.config.get('TWILIO_AUTH_TOKEN')),
                "whatsapp_from": current_app.config.get('TWILIO_WHATSAPP_FROM'),
                "verified_numbers": current_app.config.get('VERIFIED_NUMBERS', [])
            }
    
    @staticmethod
    def create_message_record(campaign_id, phone_number, rendered_text, provider_sid=None, error=None):
        '''Create a message record in database'''
        state = 'SENT' if provider_sid else 'FAILED'
        
        # We need template_id, so we'll get it from campaign or use a default
        from app.models.campaign import Campaign
        campaign = Campaign.get_by_id(campaign_id)
        template_id = campaign.template_id if campaign else 1
        
        message = Message(
            campaign_id=campaign_id,
            phone_number=phone_number,
            template_id=template_id,
            body=rendered_text,
            state=state,
            provider_message_sid=provider_sid or "failed",
            error_code=error
        )
        
        return message.save()