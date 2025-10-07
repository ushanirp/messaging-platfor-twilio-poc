/*
users : Holds all end-user profiles.
*/
CREATE TABLE users (
    phone_number VARCHAR(20) PRIMARY KEY,  -- E.164 format (e.g., +94771234567)
    attributes JSON,                       -- arbitrary user attributes (name, region, os, etc.)
    consent_state ENUM('PENDING','OPT_IN','OPT_OUT') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

/*
topics: A dictionary table for subscription topics
*/
CREATE TABLE topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

/*
subscriptions: (User ↔ Topic many-to-many mapping)
*/
CREATE TABLE subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    topic_id INT NOT NULL,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unsubscribed_at TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (phone_number) REFERENCES users(phone_number),
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    UNIQUE (phone_number, topic_id)
);

/*
segments: Targeting logic stored as JSON or DSL rules
*/
CREATE TABLE segments (
    segment_id INT AUTO_INCREMENT PRIMARY KEY,
    segment VARCHAR(100) UNIQUE NOT NULL,
    definition JSON NOT NULL,  -- e.g. {"country":"LK","consent":"OPT_IN","topics":["sports"]}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

/*
templates: Reusable WhatsApp message templates with placeholders
*/
CREATE TABLE templates (
    template_id INT AUTO_INCREMENT PRIMARY KEY,
    channel ENUM('whatsapp') DEFAULT 'whatsapp',
    locale VARCHAR(10) NOT NULL,           -- e.g. en_US, si_LK
    placeholders JSON NOT NULL,                 -- e.g. {"body":"Hello {{name}}, your score is {{score}}"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

/*
campaigns: Scheduled or triggered messaging campaign
*/
CREATE TABLE campaigns (
    campaign_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    template_id INT NOT NULL,
    schedule JSON NOT NULL,                -- e.g. {"start":"2025-10-05T09:00Z","end":"2025-10-07T21:00Z"}
    status ENUM('DRAFT','SCHEDULED','RUNNING','PAUSED','COMPLETED','CANCELLED') DEFAULT 'DRAFT',
    rate_limit INT DEFAULT 10,           -- max msgs per hour
    quiet_hours JSON,                      -- e.g. {"start":"22:00","end":"07:00"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    FOREIGN KEY (template_id) REFERENCES templates(template_id)
);

/*
messages: Materialized per recipient — lifecycle state machine
*/
CREATE TABLE messages (
    message_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT,
    phone_number VARCHAR(20) NOT NULL,
    template_id INT,
    body TEXT,                             -- final rendered message with placeholders replaced
    state ENUM('QUEUED','SENDING','SENT','DELIVERED','READ','FAILED','UNDLVD') DEFAULT 'QUEUED',
    provider_message_sid VARCHAR(64),      -- Twilio MessageSid
    error_code VARCHAR(10) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (phone_number) REFERENCES users(phone_number),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (template_id) REFERENCES templates(template_id)
);

/*
events_inbound: Store raw + normalized inbound messages
*/
CREATE TABLE events_inbound (
    inbound_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    raw_payload JSON NOT NULL,
    from_number VARCHAR(20) NOT NULL,
    wa_id VARCHAR(50),
    body TEXT,
    message_sid VARCHAR(64),
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*
delivery_receipts: Store raw + normalized status callbacks
*/
CREATE TABLE delivery_receipts (
    receipt_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    raw_payload JSON NOT NULL,
    message_sid VARCHAR(64) NOT NULL,
    message_status ENUM('queued','sending','sent','delivered','read','failed','undelivered') NOT NULL,
    error_code VARCHAR(10) NULL,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);