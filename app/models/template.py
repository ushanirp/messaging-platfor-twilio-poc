from app.database.connection import get_db
import json
from datetime import datetime

class Template:
    def __init__(self, template_id=None, channel='whatsapp', locale='en', 
                 placeholders=None, created_at=None, updated_at=None, is_active=True):
        self.template_id = template_id
        self.channel = channel
        self.locale = locale
        self.placeholders = placeholders or []
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = is_active
    
    def to_dict(self):
        return {
            'template_id': self.template_id,
            'channel': self.channel,
            'locale': self.locale,
            'placeholders': self.placeholders,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': bool(self.is_active)
        }
    
    def save(self):
        """Save template to database"""
        db = get_db()
        
        if self.template_id:
            # Update existing template
            db.execute(
                """UPDATE templates SET channel=?, locale=?, placeholders=?, is_active=?
                WHERE template_id=?""",
                (self.channel, self.locale, json.dumps(self.placeholders), 
                 self.is_active, self.template_id)
            )
        else:
            # Create new template - name field removed to match schema
            cursor = db.execute(
                """INSERT INTO templates (channel, locale, placeholders)
                VALUES (?, ?, ?)""",
                (self.channel, self.locale, json.dumps(self.placeholders))
            )
            self.template_id = cursor.lastrowid
        
        db.commit()
        return self
    
    @classmethod
    def get_by_id(cls, template_id):
        """Get template by ID"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM templates WHERE template_id = ?", 
            (template_id,)
        ).fetchone()
        return cls._row_to_template(row) if row else None
    
    @classmethod
    def get_all(cls):
        """Get all templates"""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM templates ORDER BY created_at DESC"
        ).fetchall()
        return [cls._row_to_template(row) for row in rows]
    
    @classmethod
    def _row_to_template(cls, row):
        """Convert database row to Template object"""
        if not row:
            return None
        
        return cls(
            template_id=row['template_id'],
            channel=row['channel'],
            locale=row['locale'],
            placeholders=json.loads(row['placeholders'] or '[]'),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            is_active=bool(row['is_active'])
        )