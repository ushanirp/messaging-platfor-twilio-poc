# messaging-platform-twilio-poc
Event-Driven Messaging Platform POC.

A robust, scalable WhatsApp messaging platform built with Flask that enables personalized campaign management, user segmentation, and message delivery via Twilio.

## Features

- **User Management** - Store users with attributes and consent preferences
- **Template System** - Dynamic message templates with placeholder support
- **Smart Segmentation** - Create user segments based on attributes
- **Campaign Management** - Schedule and launch messaging campaigns
- **Real-time Tracking** - Monitor message delivery status and analytics
- **Webhook Support** - Handle inbound messages and delivery receipts
- **Rate Limiting** - Configurable message sending rates
- **Quiet Hours** - Prevent messaging during specified hours

## Quick Start

### Prerequisites

- Python 3.8+
- Twilio Account (for WhatsApp messaging)
- SQLite (included) or PostgreSQL

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd whatsapp-messaging-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python db/init_db.py
```

6. **Run the application**
```bash
python -m app.run
```

The API will be available at `http://localhost:5000/api/v1/`

## Configuration

### Configurations - Development

Create a `config.yaml` file with the following variables:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14xxxxxxx

# Application Security
SECRET_KEY=your-secure-secret-key-here
DATABASE_PATH=app.db

# Webhook Security
TWILIO_VALIDATE_WEBHOOKS=true

# Rate Limiting & Quiet Hours
DEFAULT_RATE_LIMIT=1
DEFAULT_QUIET_START=22
DEFAULT_QUIET_END=8

# Verified Numbers (comma-separated for trial accounts)
VERIFIED_NUMBERS=+1234567890,+1987654321

# Default Admin User
DEFAULT_CREATED_BY=system
```
### Configurations - Production

Create a secret in AWS or respective cloud environment including the above mentioned variables and db access details.

### Twilio Setup

1. Create a Twilio account at [twilio.com](https://www.twilio.com)
2. Get your Account SID and Auth Token from the dashboard
3. Set up WhatsApp Sandbox following Twilio's guide
4. Configure webhooks in Twilio console:
   - Inbound: `https://yourdomain.com/api/v1/webhooks/twilio/inbound`
   - Status: `https://yourdomain.com/api/v1/webhooks/twilio/status`

## API Usage

### Basic Workflow

1. **Create Users**
```bash
curl -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+94123458986",
    "attributes": {
      "first_name": "Kavi",
      "city": "Colombo",
      "plan": "premium"
    },
    "consent": {
      "whatsapp": true
    }
  }'
```

2. **Create Template**
```bash
curl -X POST http://localhost:5000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "welcome_message",
    "body": "Hello {{ first_name }}! Welcome to {{ city }}.",
    "placeholders": ["first_name", "city"]
  }'
```

3. **Create Segment**
```bash
curl -X POST http://localhost:5000/api/v1/segments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "premium_users",
    "definition": {
      "filters": [{
        "path": "attributes.plan",
        "op": "eq",
        "value": "premium"
      }]
    }
  }'
```

4. **Create and Launch Campaign**
```bash
# Create campaign
curl -X POST http://localhost:5000/api/v1/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "premium_welcome",
    "template_id": 1,
    "segment_id": 1
  }'

# Launch campaign
curl -X POST http://localhost:5000/api/v1/campaigns/1/launch
```

### Testing Endpoints

Verify your setup:
```bash
# Check Twilio configuration
curl http://localhost:5000/api/v1/debug/twilio/verify

# View all data
curl http://localhost:5000/api/v1/debug/database

# Send test message
curl -X POST http://localhost:5000/api/v1/messages/test/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+94123458986",
    "message": "Test message from API"
  }'
```

## Database Management

### Reset Database
```bash
# Complete reset (drops all data)
python scripts/reset_db.py

# Clear data only (keeps table structure)
python scripts/clear_data.py
```

### Database Schema
The application uses the following tables:
- `users` - User profiles and consent
- `templates` - Message templates
- `segments` - User segment definitions
- `campaigns` - Campaign configurations
- `messages` - Message delivery tracking
- `delivery_receipts` - Webhook delivery data
- `inbound_events` - Inbound message tracking

## Deployment

### Production Deployment

1. **Set production environment**
```bash
export FLASK_ENV=production
```

2. **Use production database**
```bash
export DATABASE_PATH=/var/lib/yourapp/app.db
```

3. **Enable webhook validation**
```bash
export TWILIO_VALIDATE_WEBHOOKS=true
```

### Deployment Options

#### Option 1: Traditional VPS (Ubuntu)
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Set up application
mkdir -p /var/www/yourapp
cd /var/www/yourapp

# Configure nginx
sudo nano /etc/nginx/sites-available/yourapp

# Set up systemd service
sudo nano /etc/systemd/system/yourapp.service
```

#### Option 2: Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

#### Option 3: Cloud Platforms

**Heroku:**
```bash
# Procfile
web: python run.py

# Runtime
python-3.9.0
```

**AWS Elastic Beanstalk:**
```bash
# requirements.txt must be present
# .ebextensions/python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: run:app
```

## Development

### Project Structure
```
whatsapp-messaging-platform/
├── app/
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── api/            # REST API endpoints
│   ├── database/       # Database connection
│   └── utils/          # Utilities
├── db/                 # Database management 
│   ├──scripts/         # Database scripts
├── config/            # Configuration files
└── requirements.txt   # Dependencies
```

### Adding New Features

1. **Create model** in `app/models/`
2. **Add service logic** in `app/services/`
3. **Create API endpoints** in `app/api/v1/`
4. **Update database schema** in `db/init_db.py`

### Testing
```bash
# Run tests (add your test framework)
python -m pytest tests/

# Test specific endpoint
curl http://localhost:5000/api/v1/debug/twilio/verify
```

## Monitoring & Logs

### Access Logs
```bash
# Development
tail -f logs/development.log

# Production
journalctl -u yourapp.service -f
```

### Health Checks
```bash
# API health
curl http://localhost:5000/api/v1/debug/twilio/verify

# Database health
curl http://localhost:5000/api/v1/debug/database
```

## Security

- Config file contains sensitive data in Dev envrionment, secret based implementation for production.
- SQL injection protection via parameterized queries
- CORS configuration for frontend integration
- Rate limiting on campaign messaging
- Webhook signature validation

