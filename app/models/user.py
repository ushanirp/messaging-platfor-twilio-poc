from app.database.connection import get_db
import json
from app.utils.phone_utils import normalize_phone, validate_e164

class User:
    def __init__(self, phone_number=None, attributes=None, consent_state='PENDING', 
                 created_at=None, updated_at=None, is_active=True):
        self.phone_number = phone_number
        self.attributes = attributes or {}
        self.consent_state = consent_state
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = is_active
    
    def to_dict(self):
        return {
            'phone_number': self.phone_number,
            'attributes': self.attributes,
            'consent_state': self.consent_state,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': bool(self.is_active)
        }
    
    @classmethod
    def create_or_update(cls, phone, attributes=None, consent=None):
        """Create or update user by phone"""
        db = get_db()
        normalized_phone = normalize_phone(phone)
        
        if not validate_e164(normalized_phone):
            raise ValueError("Invalid phone number")
        
        # Convert consent dict to consent_state
        consent_state = 'PENDING'
        if consent and consent.get('whatsapp') is False:
            consent_state = 'OPT_OUT'
        elif consent and consent.get('whatsapp') is True:
            consent_state = 'OPT_IN'
        
        attributes_json = json.dumps(attributes or {})
        
        # Check if user exists
        existing = db.execute(
            "SELECT phone_number FROM users WHERE phone_number = ?", 
            (normalized_phone,)
        ).fetchone()
        
        if existing:
            # Update existing user
            db.execute(
                """UPDATE users SET attributes = ?, consent_state = ?, is_active = ? 
                WHERE phone_number = ?""",
                (attributes_json, consent_state, True, normalized_phone)
            )
        else:
            # Create new user
            db.execute(
                """INSERT INTO users (phone_number, attributes, consent_state) 
                VALUES (?, ?, ?)""",
                (normalized_phone, attributes_json, consent_state)
            )
        
        db.commit()
        return cls.get_by_phone(normalized_phone)
    
    @classmethod
    def get_by_phone(cls, phone):
        """Get user by phone"""
        db = get_db()
        normalized_phone = normalize_phone(phone)
        row = db.execute(
            "SELECT * FROM users WHERE phone_number = ?", 
            (normalized_phone,)
        ).fetchone()
        return cls._row_to_user(row) if row else None
    
    @classmethod
    def get_all(cls):
        """Get all users"""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ).fetchall()
        return [cls._row_to_user(row) for row in rows]
    
    @classmethod
    def _row_to_user(cls, row):
        """Convert database row to User object"""
        if not row:
            return None
        
        return cls(
            phone_number=row['phone_number'],
            attributes=json.loads(row['attributes'] or '{}'),
            consent_state=row['consent_state'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            is_active=bool(row['is_active'])
        )