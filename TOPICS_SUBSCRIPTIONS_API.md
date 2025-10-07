# API Documentation

## Overview
A robust WhatsApp messaging platform built with Flask that enables personalized campaign management, user segmentation, and message delivery via Twilio. Provides complete CRUD operations for users, templates, segments, and campaigns with real-time message tracking.

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
Currently uses simple API key authentication (to be implemented). All endpoints require proper authorization headers.

---

## Endpoints

### Users Management

#### Get All Users
**GET** `/users`
Retrieve all users in the system.

**Response:**
```json
[
  {
    "id": 1,
    "phone": "+94123458986",
    "attributes": {
      "first_name": "Ush",
      "city": "Colombo"
    },
    "consent": {
      "whatsapp": true
    },
    "created_at": "2025-10-02 12:00:00"
  }
]
```

#### Create/Update User
**POST** `/users`
Create a new user or update existing user by phone number.

**Request:**
```json
{
  "phone": "+94123458986",
  "attributes": {
    "first_name": "Ush",
    "last_name": "Perera",
    "city": "Colombo",
    "plan": "premium"
  },
  "consent": {
    "whatsapp": true,
    "email": false,
    "sms": true
  }
}
```

#### Bulk Users Upload
**POST** `/users/bulk`
Create or update multiple users via JSON array or CSV file.

**Request (JSON):**
```json
[
  {
    "phone": "+94123458986",
    "attributes": {"first_name": "Ush", "city": "Colombo"},
    "consent": {"whatsapp": true}
  },
  {
    "phone": "+94769876543",
    "attributes": {"first_name": "Saman", "city": "Kandy"},
    "consent": {"whatsapp": true}
  }
]
```

**Request (CSV):**
```csv
phone,attributes,consent
+94123458986,"{""first_name"":""Ush"",""city"":""Colombo""}","{""whatsapp"":true}"
+94769876543,"{""first_name"":""Saman"",""city"":""Kandy""}","{""whatsapp"":true}"
```

---

### Templates Management

#### Get All Templates
**GET** `/templates`
Retrieve all message templates.

**Response:**
```json
[
  {
    "id": 1,
    "name": "welcome_message",
    "channel": "whatsapp",
    "locale": "en",
    "body": "Hello {{ first_name }}! Welcome to our service.",
    "placeholders": ["first_name"],
    "created_at": "2025-10-02 12:00:00"
  }
]
```

#### Get Template by ID
**GET** `/templates/{id}`
Retrieve a specific template.

#### Create Template
**POST** `/templates`
Create a new message template.

**Request:**
```json
{
  "name": "premium_offer",
  "channel": "whatsapp",
  "locale": "en",
  "body": "Hi {{ first_name }}! You're on our {{ plan }} plan. Exclusive offer: {{ offer_details }}",
  "placeholders": ["first_name", "plan", "offer_details"]
}
```

#### Preview Template
**POST** `/templates/{id}/preview`
Preview how a template renders with actual data.

**Request:**
```json
{
  "placeholders": {
    "first_name": "Ush",
    "plan": "premium",
    "offer_details": "50% discount on premium features"
  }
}
```

**Response:**
```json
{
  "rendered": "Hi Ush! You're on our premium plan. Exclusive offer: 50% discount on premium features"
}
```

---

### Segments Management

#### Get All Segments
**GET** `/segments`
Retrieve all user segments.

**Response:**
```json
[
  {
    "id": 1,
    "name": "premium_users",
    "definition": {
      "filters": [
        {
          "path": "attributes.plan",
          "op": "eq",
          "value": "premium"
        }
      ]
    },
    "created_at": "2025-10-02 12:00:00"
  }
]
```

#### Get Segment by ID
**GET** `/segments/{id}`
Retrieve a specific segment.

#### Create Segment
**POST** `/segments`
Create a new user segment with filter definitions.

**Request:**
```json
{
  "name": "colombo_premium_users",
  "definition": {
    "filters": [
      {
        "path": "attributes.plan",
        "op": "eq",
        "value": "premium"
      },
      {
        "path": "attributes.city",
        "op": "eq", 
        "value": "Colombo"
      }
    ]
  }
}
```

#### Get Segment Members
**GET** `/segments/{id}/members`
Retrieve all users who match the segment criteria.

**Response:**
```json
{
  "count": 2,
  "members": [
    {
      "id": 1,
      "phone": "+94123458986",
      "attributes": {
        "first_name": "Ush",
        "plan": "premium",
        "city": "Colombo"
      },
      "consent": {"whatsapp": true},
      "created_at": "2025-10-02 12:00:00"
    }
  ]
}
```
---
## Topics Management

### Create Topic
**POST** `/topics`  
Create a new topic.

**Request:**
```json
{
  "topic": "new_feature"
}
```

**Response:**
```json
{
  "topic_id": 3,
  "topic": "new_feature",
  "created_at": "2025-10-07 18:00:00",
  "updated_at": "2025-10-07 18:00:00"
}
```

**Curl:**
```bash
curl -X POST http://localhost:5000/api/v1/topics -H "Content-Type: application/json" -d '{"topic":"new_feature"}'
```

---

### Get All Topics
**GET** `/topics`  
Fetch all topics (optionally only active).

**Response:**
```json
[
  {
    "topic_id": 1,
    "topic": "onboarding",
    "created_at": "2025-10-02 12:00:00",
    "updated_at": "2025-10-02 12:00:00"
  },
  {
    "topic_id": 3,
    "topic": "new_feature",
    "created_at": "2025-10-07 18:00:00",
    "updated_at": "2025-10-07 18:00:00"
  }
]
```

**Curl:**
```bash
curl http://localhost:5000/api/v1/topics
```

---

### Get Specific Topic
**GET** `/topics/{topic_id}`  

**Response:**
```json
{
  "topic_id": 3,
  "topic": "new_feature",
  "created_at": "2025-10-07 18:00:00",
  "updated_at": "2025-10-07 18:00:00"
}
```

**Curl:**
```bash
curl http://localhost:5000/api/v1/topics/3
```

---

### Update Topic
**PUT** `/topics/{topic_id}`  

**Request:**
```json
{
  "topic": "updated_feature"
}
```

**Response:**
```json
{
  "topic_id": 3,
  "topic": "updated_feature",
  "created_at": "2025-10-07 18:00:00",
  "updated_at": "2025-10-07 18:15:00"
}
```

**Curl:**
```bash
curl -X PUT http://localhost:5000/api/v1/topics/3 -H "Content-Type: application/json" -d '{"topic":"updated_feature"}'
```

---

### Delete / Deactivate Topic
**DELETE** `/topics/{topic_id}`  

**Response:**
```json
{
  "success": true,
  "message": "Topic deactivated"
}
```

**Curl:**
```bash
curl -X DELETE http://localhost:5000/api/v1/topics/3
```

---

## Subscriptions Management

### Subscribe User to Topic
**POST** `/subscriptions`  

**Request:**
```json
{
  "phone_number": "+94123458986",
  "topic_id": 1
}
```

**Response:**
```json
{
  "subscription_id": 10,
  "phone_number": "+94123458986",
  "topic_id": 1,
  "subscribed_at": "2025-10-07 18:20:00",
  "unsubscribed_at": null
}
```

**Curl:**
```bash
curl -X POST http://localhost:5000/api/v1/subscriptions -H "Content-Type: application/json" -d '{"phone_number":"+94123458986","topic_id":1}'
```

---

### Unsubscribe User from Topic
**DELETE** `/subscriptions/{subscription_id}`  

**Response:**
```json
{
  "success": true,
  "message": "User unsubscribed from topic"
}
```

**Curl:**
```bash
curl -X DELETE http://localhost:5000/api/v1/subscriptions/10
```

---

### Get User Subscriptions
**GET** `/subscriptions?phone_number=+94123458986`  

**Response:**
```json
[
  {
    "subscription_id": 10,
    "phone_number": "+94123458986",
    "topic_id": 1,
    "topic": "onboarding",
    "subscribed_at": "2025-10-07 18:20:00",
    "unsubscribed_at": null
  }
]
```

**Curl:**
```bash
curl "http://localhost:5000/api/v1/subscriptions?phone_number=+94123458986"
```

---

### Get Topic Subscribers
**GET** `/subscriptions?topic_id=1`  

**Response:**
```json
[
  {
    "subscription_id": 10,
    "phone_number": "+94123458986",
    "topic_id": 1,
    "subscribed_at": "2025-10-07 18:20:00",
    "unsubscribed_at": null
  }
]
```

**Curl:**
```bash
curl "http://localhost:5000/api/v1/subscriptions?topic_id=1"
```

---

### Campaigns Management

#### Get All Campaigns
**GET** `/campaigns`
Retrieve all campaigns.

**Response:**
```json
[
  {
    "id": 1,
    "name": "welcome_campaign",
    "topic": "onboarding",
    "template_id": 1,
    "segment_id": 1,
    "schedule_type": "immediate",
    "schedule_at": null,
    "status": "completed",
    "rate_limit_per_second": 2,
    "quiet_start": 22,
    "quiet_end": 8,
    "timezone": "UTC",
    "created_by": "admin",
    "created_at": "2025-10-02 12:00:00"
  }
]
```

#### Get Campaign by ID
**GET** `/campaigns/{id}`
Retrieve a specific campaign.

#### Create Campaign
**POST** `/campaigns`
Create a new messaging campaign.

**Request:**
```json
{
  "name": "premium_onboarding",
  "topic_id": 1,
  "template_id": 1,
  "segment_id": 1,
  "schedule_type": "immediate",
  "schedule_at": "2025-10-03 10:00:00",
  "rate_limit_per_second": 2,
  "quiet_start": 22,
  "quiet_end": 8,
  "timezone": "Asia/Colombo",
  "created_by": "admin"
}
```

#### Launch Campaign
**POST** `/campaigns/{id}/launch`
Start message delivery for a campaign.

**Response:**
```json
{
  "queued": 150,
  "sent": 148
}
```

#### Get Campaign Status
**GET** `/campaigns/{id}/status`
Get detailed status and message counts for a campaign.

**Response:**
```json
{
  "campaign": {
    "id": 1,
    "name": "welcome_campaign",
    "status": "completed"
  },
  "total": 150,
  "counts": {
    "queued": 0,
    "sending": 0,
    "sent": 148,
    "delivered": 145,
    "failed": 2,
    "undeliverable": 0
  }
}
```

---

### Messages Management

#### Get Messages
**GET** `/messages`
Retrieve all messages with optional campaign filtering.

**Query Parameters:**
- `campaign_id` (optional): Filter by campaign

**Response:**
```json
[
  {
    "id": 1,
    "campaign_id": 1,
    "user_id": 1,
    "rendered_text": "Hi Ush! Welcome to our premium plan.",
    "state": "delivered",
    "provider": "twilio",
    "provider_sid": "SM1234567890",
    "attempts": 1,
    "last_attempt_at": "2025-10-02 12:05:00",
    "error": null,
    "created_at": "2025-10-02 12:00:00"
  }
]
```

#### Send Test Message
**POST** `/messages/test/send`
Send a direct WhatsApp message (bypasses campaigns).

**Request:**
```json
{
  "phone": "+94123458986",
  "message": "Hello! This is a direct test message."
}
```

**Response:**
```json
{
  "success": true,
  "message_sid": "SM1234567890"
}
```

#### Send to Verified Numbers
**POST** `/messages/test/send/verified`
Send message only to verified numbers (for Twilio trial accounts).

**Request:** Same as test send endpoint.

---

### Webhooks

#### Inbound Messages Webhook
**POST** `/webhooks/twilio/inbound`
Receive inbound WhatsApp messages from Twilio.

**Expected Twilio Payload:**
```
From: whatsapp:+94123458986
To: whatsapp:+14155238886
Body: Hello, I want to unsubscribe
MessageSid: SM1234567890
```

#### Delivery Status Webhook
**POST** `/webhooks/twilio/status`
Receive message delivery status updates from Twilio.

**Expected Twilio Payload:**
```
MessageSid: SM1234567890
MessageStatus: delivered
To: whatsapp:+94123458986
```

---

### Debug & Monitoring

#### Verify Twilio Configuration
**GET** `/debug/twilio/verify`
Check Twilio credentials and connection.

**Response:**
```json
{
  "status": "success",
  "account_sid": "AC1234567890",
  "friendly_name": "My Twilio Account",
  "status": "active",
  "type": "Full"
}
```

#### View All Database Data
**GET** `/debug/database`
Debug endpoint to view all data across all tables.

**Response:**
```json
{
  "users": [...],
  "templates": [...],
  "segments": [...],
  "campaigns": [...],
  "messages": [...]
}
```

---

## Data Models
### User
- `phone_number`: String, Primary Key, E.164 format (e.g., +94771234567)
- `attributes`: JSON, stored as string, user profile data
- `consent_state`: String, 'PENDING', 'OPT_IN', 'OPT_OUT', default 'PENDING'
- `created_at`: DateTime
- `updated_at`: DateTime
- `is_active`: Boolean, default 1

### Topic
- `topic_id`: Integer, Primary Key, Auto-increment
- `topic`: String, Unique, topic name (e.g., onboarding)
- `created_at`: DateTime
- `updated_at`: DateTime
- `is_active`: Boolean, default 1

### Subscription
- `subscription_id`: Integer, Primary Key, Auto-increment
- `phone_number`: String, Foreign Key → `users(phone_number)`
- `topic_id`: Integer, Foreign Key → `topics(topic_id)`
- `subscribed_at`: DateTime
- `unsubscribed_at`: DateTime, nullable

### Segment
- `segment_id`: Integer, Primary Key, Auto-increment
- `segment`: String, Unique, segment name
- `definition`: JSON, stored as string, filter/DSL rules
- `created_at`: DateTime
- `updated_at`: DateTime
- `is_active`: Boolean, default 1

### Template
- `template_id`: Integer, Primary Key, Auto-increment
- `channel`: String, default 'whatsapp'
- `locale`: String, e.g., en_US, si_LK
- `placeholders`: JSON Array, stored as string
- `created_at`: DateTime
- `updated_at`: DateTime
- `is_active`: Boolean, default 1

### Campaign
- `campaign_id`: Integer, Primary Key, Auto-increment
- `name`: String, Unique
- `topic_id`: Integer, Foreign Key → `topics(topic_id)`
- `template_id`: Integer, Foreign Key → `templates(template_id)`
- `schedule`: JSON, schedule details
- `status`: String, 'DRAFT','SCHEDULED','RUNNING','PAUSED','COMPLETED','CANCELLED', default 'DRAFT'
- `rate_limit`: Integer, messages per second
- `quiet_hours`: JSON, start/end hours
- `created_at`: DateTime
- `updated_at`: DateTime

### Message
- `message_id`: Integer, Primary Key
- `campaign_id`: Integer, Foreign Key → `campaigns(campaign_id)`
- `phone_number`: String, Foreign Key → `users(phone_number)`
- `template_id`: Integer, Foreign Key → `templates(template_id)`
- `body`: String, rendered message content
- `state`: String, 'QUEUED','SENDING','SENT','DELIVERED','READ','FAILED','UNDLVD'
- `provider_message_sid`: String, provider message ID
- `error_code`: String, error message if failed
- `created_at`: DateTime

### Inbound Event
- `inbound_id`: Integer, Primary Key
- `raw_payload`: String
- `from_number`: String
- `wa_id`: String
- `body`: String
- `message_sid`: String
- `timestamp`: DateTime
- `created_at`: DateTime

### Delivery Receipt
- `receipt_id`: Integer, Primary Key
- `raw_payload`: String
- `message_sid`: String
- `message_status`: String, 'queued','sending','sent','delivered','read','failed','undelivered'
- `error_code`: String
- `timestamp`: DateTime
- `created_at`: DateTime

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200` Success
- `201` Created
- `400` Bad Request (validation errors)
- `404` Not Found
- `500` Internal Server Error

**Error Response Format:**
```json
{
  "error": "Detailed error message"
}
```

---

## Rate Limiting

- Campaigns support configurable rate limiting via `rate_limit_per_second`
- Default: 1 message per second
- Configurable via environment variables

## Quiet Hours

- Prevent messaging during specified hours
- Configurable via `quiet_start` and `quiet_end` (24-hour format)
- Default: 10 PM to 8 AM