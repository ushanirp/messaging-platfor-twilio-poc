from app.database.connection import get_db

class Message:
    def __init__(self, message_id=None, campaign_id=None, phone_number=None,
                 template_id=None, body=None, state='QUEUED', provider_message_sid=None,
                 error_code=None, created_at=None, updated_at=None):
        self.message_id = message_id
        self.campaign_id = campaign_id
        self.phone_number = phone_number
        self.template_id = template_id
        self.body = body
        self.state = state
        self.provider_message_sid = provider_message_sid
        self.error_code = error_code
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self):
        return {
            'message_id': self.message_id,
            'campaign_id': self.campaign_id,
            'phone_number': self.phone_number,
            'template_id': self.template_id,
            'body': self.body,
            'state': self.state,
            'provider_message_sid': self.provider_message_sid,
            'error_code': self.error_code,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def save(self):
        """Save message to database"""
        db = get_db()
        
        if self.message_id:
            # Update existing message
            db.execute(
                """UPDATE messages SET campaign_id=?, phone_number=?, template_id=?,
                body=?, state=?, provider_message_sid=?, error_code=?
                WHERE message_id=?""",
                (self.campaign_id, self.phone_number, self.template_id, self.body,
                 self.state, self.provider_message_sid, self.error_code, self.message_id)
            )
        else:
            # Create new message
            cursor = db.execute(
                """INSERT INTO messages 
                (campaign_id, phone_number, template_id, body, state, provider_message_sid, error_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.campaign_id, self.phone_number, self.template_id, self.body,
                 self.state, self.provider_message_sid, self.error_code)
            )
            self.message_id = cursor.lastrowid
        
        db.commit()
        return self
    
    @classmethod
    def get_by_id(cls, message_id):
        """Get message by ID"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM messages WHERE message_id = ?", 
            (message_id,)
        ).fetchone()
        return cls._row_to_message(row) if row else None
    
    @classmethod
    def get_by_campaign(cls, campaign_id, limit=200):
        """Get messages by campaign ID"""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM messages WHERE campaign_id = ? ORDER BY created_at DESC LIMIT ?",
            (campaign_id, limit)
        ).fetchall()
        return [cls._row_to_message(row) for row in rows]
    
    @classmethod
    def get_all(cls, limit=200):
        """Get all messages"""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM messages ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [cls._row_to_message(row) for row in rows]
    
    @classmethod
    def _row_to_message(cls, row):
        """Convert database row to Message object"""
        if not row:
            return None
        
        return cls(
            message_id=row['message_id'],
            campaign_id=row['campaign_id'],
            phone_number=row['phone_number'],
            template_id=row['template_id'],
            body=row['body'],
            state=row['state'],
            provider_message_sid=row['provider_message_sid'],
            error_code=row['error_code'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )