from flask import Blueprint, request, jsonify
from app.models.segment import Segment
from app.services.segment_service import SegmentService

segments_bp = Blueprint('segments', __name__)

@segments_bp.route("/segments", methods=["POST"])
def create_segment():
    """Create a new segment"""
    data = request.json or {}
    name = data.get('name')
    definition = data.get('definition', {})
    
    try:
        segment = SegmentService.create_segment(name, definition)
        return jsonify(segment.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@segments_bp.route("/segments/<int:seg_id>/members", methods=["GET"])
def segment_members(seg_id):
    """Get segment members"""
    try:
        members = SegmentService.evaluate_segment_members(seg_id)
        return jsonify({
            "count": len(members),
            "members": [member.to_dict() for member in members]
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@segments_bp.route("/segments", methods=["GET"])
def get_segments():
    """Get all segments"""
    segments = Segment.get_all()
    return jsonify([segment.to_dict() for segment in segments])

@segments_bp.route("/segments/<int:seg_id>", methods=["GET"])
def get_segment(seg_id):
    """Get specific segment"""
    segment = Segment.get_by_id(seg_id)
    if not segment:
        return jsonify({"error": "Segment not found"}), 404
    return jsonify(segment.to_dict())