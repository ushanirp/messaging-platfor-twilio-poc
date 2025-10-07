from app.database.connection import get_db
from datetime import datetime
import json

class Campaign:
    def __init__(self,campaign_id=None, name=None, topic_id=None, template_id=None, 
                 schedule=None, status='DRAFT', rate_limit=10, quiet_hours=None,
                 created_at=None, updated_at=None):
        self.campaign_id = campaign_id
        self.name = name
        self.topic_id = topic_id
        self.template_id = template_id
        self.schedule = schedule or {}
        self.status = status
        self.rate_limit = rate_limit
        self.quiet_hours = quiet_hours or {}
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self):
        return {
            'campaign_id': self.campaign_id,
            'name': self.name,
            'topic_id': self.topic_id,
            'template_id': self.template_id,
            'schedule': self.schedule,
            'status': self.status,
            'rate_limit': self.rate_limit,
            'quiet_hours': self.quiet_hours,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def save(self):
        """Save campaign to database"""
        db = get_db()
        
        if self.campaign_id:
            # Update existing campaign
            db.execute(
                """UPDATE campaigns SET topic_id=?, template_id=?, schedule=?, 
                status=?, rate_limit=?, quiet_hours=? WHERE campaign_id=?""",
                (self.topic_id, self.template_id, json.dumps(self.schedule),
                 self.status, self.rate_limit, json.dumps(self.quiet_hours), 
                 self.campaign_id)
            )
        else:
            # Create new campaign
            cursor = db.execute(
                """INSERT INTO campaigns 
                (topic_id, template_id, schedule, status, rate_limit, quiet_hours)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (self.topic_id, self.template_id, json.dumps(self.schedule),
                 self.status, self.rate_limit, json.dumps(self.quiet_hours))
            )
            self.campaign_id = cursor.lastrowid
        
        db.commit()
        return self
    
    @classmethod
    def get_by_id(cls, campaign_id):
        """Get campaign by ID"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM campaigns WHERE campaign_id = ?", 
            (campaign_id,)
        ).fetchone()
        return cls._row_to_campaign(row) if row else None
    
    @classmethod
    def get_all(cls):
        """Get all campaigns"""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM campaigns ORDER BY created_at DESC"
        ).fetchall()
        return [cls._row_to_campaign(row) for row in rows]
    
    @classmethod
    def _row_to_campaign(cls, row):
        """Convert database row to Campaign object"""
        if not row:
            return None
        
        return cls(
            campaign_id=row['campaign_id'],
            topic_id=row['topic_id'],
            template_id=row['template_id'],
            schedule=json.loads(row['schedule'] or '{}'),
            status=row['status'],
            rate_limit=row['rate_limit'],
            quiet_hours=json.loads(row['quiet_hours'] or '{}'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )