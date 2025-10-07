import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    app = Flask(__name__)
    
    try:
        # Use your ConfigLoader instead of direct config imports
        from app.config_loader import ConfigLoader
        config_loader = ConfigLoader()
        
        # Load all config values into Flask app config with proper defaults
        app.config['DEBUG'] = config_loader.get('DEBUG', True)
        app.config['SECRET_KEY'] = config_loader.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['DATABASE_PATH'] = config_loader.get('DATABASE_PATH', 'db/sqlitedb/whatsapp_platform.db')
        app.config['TWILIO_ACCOUNT_SID'] = config_loader.get('TWILIO_ACCOUNT_SID', '')
        app.config['TWILIO_AUTH_TOKEN'] = config_loader.get('TWILIO_AUTH_TOKEN', '')
        app.config['TWILIO_WHATSAPP_FROM'] = config_loader.get('TWILIO_WHATSAPP_FROM', '')
        app.config['TWILIO_VALIDATE_WEBHOOKS'] = config_loader.get('TWILIO_VALIDATE_WEBHOOKS', False)
        app.config['DEFAULT_RATE_LIMIT'] = config_loader.get('DEFAULT_RATE_LIMIT', 1)
        app.config['DEFAULT_QUIET_START'] = config_loader.get('DEFAULT_QUIET_START', '22:00')
        app.config['DEFAULT_QUIET_END'] = config_loader.get('DEFAULT_QUIET_END', '08:00')
        app.config['VERIFIED_NUMBERS'] = config_loader.get('VERIFIED_NUMBERS', [])
        app.config['DEFAULT_CREATED_BY'] = config_loader.get('DEFAULT_CREATED_BY', 'system')
        
        # Validate critical config
        config_loader.validate(["SECRET_KEY", "DATABASE_PATH"])
        
    except Exception as e:
        print(f"Config loading error: {e}")
        print("Using fallback configuration...")
        # Fallback configuration
        app.config['DEBUG'] = True
        app.config['SECRET_KEY'] = 'fallback-secret-key'
        app.config['DATABASE_PATH'] = 'db/sqlitedb/whatsapp_platform.db'
        app.config['TWILIO_ACCOUNT_SID'] = ''
        app.config['TWILIO_AUTH_TOKEN'] = ''
        app.config['TWILIO_WHATSAPP_FROM'] = ''
        app.config['TWILIO_VALIDATE_WEBHOOKS'] = False
        app.config['DEFAULT_RATE_LIMIT'] = 1
        app.config['DEFAULT_QUIET_START'] = '22:00'
        app.config['DEFAULT_QUIET_END'] = '08:00'
        app.config['VERIFIED_NUMBERS'] = []
        app.config['DEFAULT_CREATED_BY'] = 'system'
    
    # Enable CORS for React frontend
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"])
    
    # Initialize database (import here to avoid circular imports)
    from app.database.connection import init_app as init_db
    init_db(app)
    
    # Force database connection to trigger table creation on app startup
    with app.app_context():
        from app.database.connection import get_db
        db = get_db()  # This will trigger table creation if needed
        print("Database connection established and tables verified")
    
    # Register API blueprints
    from app.api.routes import register_blueprints
    register_blueprints(app)
    
    return app