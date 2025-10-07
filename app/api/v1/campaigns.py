from flask import Blueprint, request, jsonify, current_app
from app.models.campaign import Campaign
from app.services.campaign_service import CampaignService

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route("/campaigns", methods=["POST"])
def create_campaign():
    """Create a new campaign"""
    data = request.json or {}
    
    try:
        campaign = CampaignService.create_campaign(
            name=data.get('name'),
            template_id=data.get('template_id'),
            segment_id=data.get('segment_id'),
            schedule_type=data.get('schedule_type', 'immediate'),
            schedule_at=data.get('schedule_at'),
            topic_id=data.get('topic_id', 'general'),
            rate_limit=data.get('rate_limit_per_second'),
            quiet_start=data.get('quiet_start'),
            quiet_end=data.get('quiet_end'),
            timezone=data.get('timezone', 'UTC'),
            created_by=data.get('created_by')
        )
        return jsonify(campaign.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@campaigns_bp.route("/campaigns/<int:cid>/launch", methods=["POST"])
def launch_campaign(cid):
    """Launch a campaign"""
    try:
        result = CampaignService.launch_campaign(cid)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@campaigns_bp.route("/campaigns/<int:cid>/status", methods=["GET"])
def campaign_status(cid):
    """Get campaign status"""
    try:
        status = CampaignService.get_campaign_status(cid)
        return jsonify(status)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@campaigns_bp.route("/campaigns", methods=["GET"])
def get_campaigns():
    """Get all campaigns"""
    campaigns = Campaign.get_all()
    return jsonify([campaign.to_dict() for campaign in campaigns])

@campaigns_bp.route("/campaigns/<int:camp_id>", methods=["GET"])
def get_campaign(camp_id):
    """Get specific campaign"""
    campaign = Campaign.get_by_id(camp_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify(campaign.to_dict())