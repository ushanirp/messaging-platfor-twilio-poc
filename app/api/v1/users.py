import csv
import io
import json
from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.phone_utils import normalize_phone, validate_e164

users_bp = Blueprint('users', __name__)

@users_bp.route("/users", methods=["POST"])
def create_user():
    """Create or update a user"""
    data = request.json or {}
    phone = data.get('phone')
    if not phone:
        return jsonify({"error": "missing phone"}), 400
    
    attributes = data.get('attributes', {})
    consent = data.get('consent', {})
    
    try:
        user = User.create_or_update(phone, attributes, consent)
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@users_bp.route("/users/bulk", methods=["POST"])
def bulk_users():
    """Bulk create/update users from CSV or JSON"""
    created = 0
    
    if 'file' in request.files:
        # Handle CSV upload
        f = request.files['file']
        data = f.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(data))
        
        for row in reader:
            phone_raw = row.get('phone') or row.get('phone_number') or row.get('mobile')
            if not phone_raw:
                continue
            
            try:
                phone = normalize_phone(phone_raw)
                if not validate_e164(phone):
                    continue
                
                # Parse attributes and consent
                attrs = {}
                if 'attributes' in row and row['attributes']:
                    try:
                        attrs = json.loads(row['attributes'])
                    except Exception:
                        attrs = {}
                
                consent_data = {}
                if 'consent' in row and row['consent']:
                    try:
                        consent_data = json.loads(row['consent'])
                    except Exception:
                        consent_data = {}
                
                # Create or update user
                existing = User.get_by_phone(phone)
                if not existing:
                    created += 1
                
                User.create_or_update(phone, attrs, consent_data)
                
            except Exception:
                continue
        
        return jsonify({"created": created}), 201
    
    else:
        # Handle JSON array
        arr = request.json or []
        for entry in arr:
            phone_raw = entry.get('phone')
            if not phone_raw:
                continue
            
            try:
                phone = normalize_phone(phone_raw)
                if not validate_e164(phone):
                    continue
                
                attrs = entry.get('attributes', {})
                consent_data = entry.get('consent', {})
                
                existing = User.get_by_phone(phone)
                if not existing:
                    created += 1
                
                User.create_or_update(phone, attrs, consent_data)
                
            except Exception:
                continue
        
        return jsonify({"created": created}), 201

@users_bp.route("/users", methods=["GET"])
def get_users():
    """Get all users"""
    users = User.get_all()
    return jsonify([user.to_dict() for user in users])