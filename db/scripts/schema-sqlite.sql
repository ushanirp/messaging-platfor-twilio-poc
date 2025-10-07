/*
SQLite, foreign key constraints are not enforced by default.
*/
PRAGMA foreign_keys = ON;

/*
users : Holds all end-user profiles.
*/
CREATE TABLE IF NOT EXISTS users (
    phone_number TEXT PRIMARY KEY,  -- E.164 format (e.g., +94771234567)
    attributes TEXT,                -- JSON stored as TEXT
    consent_state TEXT CHECK(consent_state IN ('PENDING','OPT_IN','OPT_OUT')) DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TRIGGER IF NOT EXISTS trg_users_updated
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE phone_number = OLD.phone_number;
END;

-- CREATE INDEX IF NOT EXISTS idx_users_consent ON users(consent_state);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

/*
topics: A dictionary table for subscription topics
*/
CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

INSERT INTO topics (topic) VALUES ('onboarding');

CREATE TRIGGER IF NOT EXISTS trg_topics_updated
AFTER UPDATE ON topics
FOR EACH ROW
BEGIN
    UPDATE topics SET updated_at = CURRENT_TIMESTAMP WHERE topic_id = OLD.topic_id;
END;

CREATE INDEX IF NOT EXISTS idx_topics_active ON topics(is_active);

/*
subscriptions: (User ↔ Topic many-to-many mapping)
*/
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    topic_id INTEGER NOT NULL,
    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    unsubscribed_at DATETIME DEFAULT NULL,
    FOREIGN KEY (phone_number) REFERENCES users(phone_number),
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    UNIQUE (phone_number, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(phone_number);
CREATE INDEX IF NOT EXISTS idx_subscriptions_topic ON subscriptions(topic_id);

/*
segments: Targeting logic stored as JSON or DSL rules
*/
CREATE TABLE IF NOT EXISTS segments (
    segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    segment TEXT UNIQUE NOT NULL,
    definition TEXT NOT NULL,  -- JSON as TEXT
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TRIGGER IF NOT EXISTS trg_segments_updated
AFTER UPDATE ON segments
FOR EACH ROW
BEGIN
    UPDATE segments SET updated_at = CURRENT_TIMESTAMP WHERE segment_id = OLD.segment_id;
END;

/*
templates: Reusable WhatsApp message templates with placeholders
*/
CREATE TABLE IF NOT EXISTS templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT CHECK(channel IN ('whatsapp')) DEFAULT 'whatsapp',
    locale TEXT NOT NULL,          -- e.g. en_US, si_LK
    placeholders TEXT NOT NULL,    -- JSON as TEXT
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TRIGGER IF NOT EXISTS trg_templates_updated
AFTER UPDATE ON templates
FOR EACH ROW
BEGIN
    UPDATE templates SET updated_at = CURRENT_TIMESTAMP WHERE template_id = OLD.template_id;
END;

/*
campaigns: Scheduled or triggered messaging campaign
*/
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    topic_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    schedule TEXT NOT NULL,  -- JSON as TEXT
    status TEXT CHECK(status IN ('DRAFT','SCHEDULED','RUNNING','PAUSED','COMPLETED','CANCELLED')) DEFAULT 'DRAFT',
    rate_limit INTEGER DEFAULT 10,
    quiet_hours TEXT,        -- JSON as TEXT
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    FOREIGN KEY (template_id) REFERENCES templates(template_id)
);

CREATE TRIGGER IF NOT EXISTS trg_campaigns_updated
AFTER UPDATE ON campaigns
FOR EACH ROW
BEGIN
    UPDATE campaigns SET updated_at = CURRENT_TIMESTAMP WHERE campaign_id = OLD.campaign_id;
END;

CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);

/*
messages: Materialized per recipient — lifecycle state machine
*/
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    phone_number TEXT NOT NULL,
    template_id INTEGER NOT NULL,
    body TEXT,
    state TEXT CHECK(state IN ('QUEUED','SENDING','SENT','DELIVERED','READ','FAILED','UNDLVD')) DEFAULT 'QUEUED',
    provider_message_sid TEXT NOT NULL,
    error_code TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (phone_number) REFERENCES users(phone_number),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (template_id) REFERENCES templates(template_id)
);

CREATE TRIGGER IF NOT EXISTS trg_messages_updated
AFTER UPDATE ON messages
FOR EACH ROW
BEGIN
    UPDATE messages SET updated_at = CURRENT_TIMESTAMP WHERE message_id = OLD.message_id;
END;

-- CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(phone_number);
-- CREATE INDEX IF NOT EXISTS idx_messages_state ON messages(state);
-- CREATE INDEX IF NOT EXISTS idx_messages_provider_sid ON messages(provider_message_sid);

/*
events_inbound: Store raw + normalized inbound messages (what users send back)
*/
CREATE TABLE IF NOT EXISTS events_inbound (
    inbound_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_payload TEXT NOT NULL,
    from_number TEXT NOT NULL,
    wa_id TEXT,
    body TEXT,
    message_sid TEXT,
    timestamp DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inbound_from ON events_inbound(from_number);
CREATE INDEX IF NOT EXISTS idx_inbound_msgsid ON events_inbound(message_sid);

/*
delivery_receipts: Store raw + normalized status callbacks
*/
CREATE TABLE IF NOT EXISTS delivery_receipts (
    receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_payload TEXT NOT NULL,
    message_sid TEXT NOT NULL,
    message_status TEXT CHECK(message_status IN ('queued','sending','sent','delivered','read','failed','undelivered')) NOT NULL,
    error_code TEXT,
    timestamp DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_receipts_msgsid ON delivery_receipts(message_sid);
CREATE INDEX IF NOT EXISTS idx_receipts_status ON delivery_receipts(message_status);
