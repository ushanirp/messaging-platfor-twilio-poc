from app.database.connection import get_db
import json
from datetime import datetime

class Segment:
    def __init__(self, segment_id=None, segment=None, definition=None, 
                 created_at=None, updated_at=None, is_active=True):
        self.segment_id = segment_id
        self.segment = segment
        self.definition = definition or {}
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = is_active
    
    def to_dict(self):
        return {
            'segment_id': self.segment_id,
            'segment': self.segment,
            'definition': self.definition,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': bool(self.is_active)
        }
    
    def save(self):
        """Save segment to database"""
        db = get_db()
        
        if self.segment_id:
            # Update existing segment
            db.execute(
                "UPDATE segments SET segment=?, definition=?, is_active=? WHERE segment_id=?",
                (self.segment, json.dumps(self.definition), self.is_active, self.segment_id)
            )
        else:
            # Create new segment
            if not self.segment:
                self.segment = f"segment_{int(datetime.utcnow().timestamp())}"
            
            cursor = db.execute(
                "INSERT INTO segments (segment, definition) VALUES (?, ?)",
                (self.segment, json.dumps(self.definition))
            )
            self.segment_id = cursor.lastrowid
        
        db.commit()
        return self
    
    @classmethod
    def get_by_id(cls, segment_id):
        """Get segment by ID"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM segments WHERE segment_id = ?", 
            (segment_id,)
        ).fetchone()
        return cls._row_to_segment(row) if row else None
    
    @classmethod
    def get_all(cls):
        """Get all segments"""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM segments ORDER BY created_at DESC"
        ).fetchall()
        return [cls._row_to_segment(row) for row in rows]
    
    @classmethod
    def _row_to_segment(cls, row):
        """Convert database row to Segment object"""
        if not row:
            return None
        
        return cls(
            segment_id=row['segment_id'],
            segment=row['segment'],
            definition=json.loads(row['definition'] or '{}'),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            is_active=bool(row['is_active'])
        )