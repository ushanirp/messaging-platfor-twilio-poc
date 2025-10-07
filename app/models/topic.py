from app.database.connection import get_db
import datetime

class Topic:
    def __init__(self, topic_id=None, topic=None, created_at=None, updated_at=None, is_active=True):
        self.topic_id = topic_id
        self.topic = topic
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = is_active

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            "topic": self.topic,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": bool(self.is_active)
        }

    # ---------------------------
    # CRUD Methods
    # ---------------------------
    @classmethod
    def create(cls, topic, is_active=True):
        """Create a new topic"""
        db = get_db()
        db.execute(
            "INSERT OR IGNORE INTO topics (topic, is_active) VALUES (?, ?)",
            (topic, 1 if is_active else 0)
        )
        db.commit()
        return cls.get_by_name(topic)

    @classmethod
    def get_by_name(cls, topic):
        """Get topic by name"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM topics WHERE topic = ?",
            (topic,)
        ).fetchone()
        return cls._row_to_topic(row)

    @classmethod
    def get_all(cls, active_only=True):
        """Fetch all topics"""
        db = get_db()
        query = (
            "SELECT * FROM topics WHERE is_active = 1 ORDER BY created_at DESC"
            if active_only
            else "SELECT * FROM topics ORDER BY created_at DESC"
        )
        rows = db.execute(query).fetchall()
        return [cls._row_to_topic(r) for r in rows]

    @classmethod
    def deactivate(cls, topic_id):
        """Soft delete (set is_active = 0)"""
        db = get_db()
        db.execute(
            "UPDATE topics SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE topic_id = ?",
            (topic_id,) 
        )
        db.commit()

    @classmethod
    def _row_to_topic(cls, row):
        if not row:
            return None
        return cls(
            topic_id=row["topic_id"],
            topic=row["topic"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            is_active=row["is_active"]
        )
