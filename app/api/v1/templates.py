from flask import Blueprint, request, jsonify
from app.models.template import Template
from app.services.template_service import TemplateService

templates_bp = Blueprint('templates', __name__)

@templates_bp.route("/templates", methods=["POST"])
def create_template():
    """Create a new template"""
    data = request.json or {}
    name = data.get('name')
    body = data.get('body', '')
    placeholders = data.get('placeholders', [])
    channel = data.get('channel', 'whatsapp')
    locale = data.get('locale', 'en')
    
    try:
        template = TemplateService.create_template(name, body, placeholders, channel, locale)
        return jsonify(template.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@templates_bp.route("/templates/<int:tpl_id>/preview", methods=["POST"])
def preview_template(tpl_id):
    """Preview template rendering"""
    data = request.json or {}
    placeholders = data.get('placeholders', {})
    
    try:
        rendered = TemplateService.preview_template(tpl_id, placeholders)
        return jsonify({"rendered": rendered})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@templates_bp.route("/templates", methods=["GET"])
def get_templates():
    """Get all templates"""
    templates = Template.get_all()
    return jsonify([template.to_dict() for template in templates])

@templates_bp.route("/templates/<int:tpl_id>", methods=["GET"])
def get_template(tpl_id):
    """Get specific template"""
    template = Template.get_by_id(tpl_id)
    if not template:
        return jsonify({"error": "Template not found"}), 404
    return jsonify(template.to_dict())