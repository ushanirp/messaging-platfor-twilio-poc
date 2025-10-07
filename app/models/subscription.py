from app.database.connection import get_db
from datetime import datetime

class Subscription:
    def __init__(self, subscription_id=None, phone_number=None, topic_id=None,
                 subscribed_at=None, unsubscribed_at=None):
        self.subscription_id = subscription_id
        self.phone_number = phone_number
        self.topic_id = topic_id
        self.subscribed_at = subscribed_at
        self.unsubscribed_at = unsubscribed_at

    def to_dict(self):
        return {
            "subscription_id": self.subscription_id,
            "phone_number": self.phone_number,
            "topic_id": self.topic_id,
            "subscribed_at": self.subscribed_at,
            "unsubscribed_at": self.unsubscribed_at
        }

    # ---------------------------
    # CRUD / Mapping Methods
    # ---------------------------
    @classmethod
    def create(cls, phone_number, topic_id):
        """Subscribe a user to a topic"""
        db = get_db()
        db.execute(
            """INSERT OR REPLACE INTO subscriptions (phone_number, topic_id, subscribed_at, unsubscribed_at)
               VALUES (?, ?, CURRENT_TIMESTAMP, NULL)""",
            (phone_number, topic_id)
        )
        db.commit()
        return cls.get(phone_number, topic_id)

    @classmethod
    def unsubscribe(cls, phone_number, topic_id):
        """Mark as unsubscribed"""
        db = get_db()
        db.execute(
            """UPDATE subscriptions SET unsubscribed_at = CURRENT_TIMESTAMP
               WHERE phone_number = ? AND topic_id = ?""",
            (phone_number, topic_id)
        )
        db.commit()

    @classmethod
    def get(cls, phone_number, topic_id):
        """Get single subscription"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM subscriptions WHERE phone_number = ? AND topic_id = ?",
            (phone_number, topic_id)
        ).fetchone()
        return cls._row_to_subscription(row)

    @classmethod
    def get_by_user(cls, phone_number):
        """All topics user subscribed to"""
        db = get_db()
        rows = db.execute(
            """SELECT s.*, t.topic FROM subscriptions s
               JOIN topics t ON s.topic_id = t.topic_id
               WHERE s.phone_number = ? AND s.unsubscribed_at IS NULL""",
            (phone_number,)
        ).fetchall()
        return [cls._row_to_subscription(r) for r in rows]

    @classmethod
    def get_all(cls):
        """List all subscriptions"""
        db = get_db()
        rows = db.execute(
            "SELECT * FROM subscriptions"
        ).fetchall()
        return [cls._row_to_subscription(r) for r in rows]

    @classmethod
    def _row_to_subscription(cls, row):
        if not row:
            return None
        return cls(
            subscription_id=row["subscription_id"],
            phone_number=row["phone_number"],
            topic_id=row["topic_id"],
            subscribed_at=row["subscribed_at"],
            unsubscribed_at=row["unsubscribed_at"]
        )
