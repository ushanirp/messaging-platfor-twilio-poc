from app.database.connection import get_db
import json

class DeliveryReceipt:
    def __init__(self, receipt_id=None, raw_payload=None, message_sid=None, 
                 message_status=None, error_code=None, timestamp=None, created_at=None):
        self.receipt_id = receipt_id
        self.raw_payload = raw_payload
        self.message_sid = message_sid
        self.message_status = message_status
        self.error_code = error_code
        self.timestamp = timestamp
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'receipt_id': self.receipt_id,
            'raw_payload': self.raw_payload,
            'message_sid': self.message_sid,
            'message_status': self.message_status,
            'error_code': self.error_code,
            'timestamp': self.timestamp,
            'created_at': self.created_at
        }
    
    def save(self):
        """Save delivery receipt to database"""
        db = get_db()
        
        cursor = db.execute(
            """INSERT INTO delivery_receipts 
            (raw_payload, message_sid, message_status, error_code, timestamp)
            VALUES (?, ?, ?, ?, ?)""",
            (json.dumps(self.raw_payload) if self.raw_payload else None,
             self.message_sid, self.message_status, self.error_code, self.timestamp)
        )
        self.receipt_id = cursor.lastrowid
        db.commit()
        return self

class InboundEvent:
    def __init__(self, inbound_id=None, raw_payload=None, from_number=None, 
                 wa_id=None, body=None, message_sid=None, timestamp=None, created_at=None):
        self.inbound_id = inbound_id
        self.raw_payload = raw_payload
        self.from_number = from_number
        self.wa_id = wa_id
        self.body = body
        self.message_sid = message_sid
        self.timestamp = timestamp
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'inbound_id': self.inbound_id,
            'raw_payload': self.raw_payload,
            'from_number': self.from_number,
            'wa_id': self.wa_id,
            'body': self.body,
            'message_sid': self.message_sid,
            'timestamp': self.timestamp,
            'created_at': self.created_at
        }
    
    def save(self):
        """Save inbound event to database"""
        db = get_db()
        
        cursor = db.execute(
            """INSERT INTO events_inbound 
            (raw_payload, from_number, wa_id, body, message_sid, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (json.dumps(self.raw_payload) if self.raw_payload else None,
             self.from_number, self.wa_id, self.body, self.message_sid, self.timestamp)
        )
        self.inbound_id = cursor.lastrowid
        db.commit()
        return self