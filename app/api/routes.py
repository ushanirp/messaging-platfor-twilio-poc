from flask import Blueprint
from app.api.v1.users import users_bp
from app.api.v1.templates import templates_bp
from app.api.v1.segments import segments_bp
from app.api.v1.campaigns import campaigns_bp
from app.api.v1.messages import messages_bp
from app.api.v1.webhooks import webhooks_bp
from app.api.v1.debug import debug_bp
from app.api.v1.topics import topics_bp
from app.api.v1.subscriptions import subscriptions_bp

def register_blueprints(app):
    """Register all API blueprints"""
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
    
    # Register version 1 blueprints
    api_v1.register_blueprint(users_bp)
    api_v1.register_blueprint(templates_bp)
    api_v1.register_blueprint(segments_bp)
    api_v1.register_blueprint(campaigns_bp)
    api_v1.register_blueprint(messages_bp)
    api_v1.register_blueprint(webhooks_bp)
    api_v1.register_blueprint(debug_bp) 
    api_v1.register_blueprint(topics_bp)
    api_v1.register_blueprint(subscriptions_bp)
    
    # Register the main API blueprint
    app.register_blueprint(api_v1)