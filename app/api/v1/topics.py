from flask import Blueprint, request, jsonify, current_app
from app.models.topic import Topic
from app.services.topic_service import TopicService

topics_bp = Blueprint('topics', __name__)

@topics_bp.route("/topics", methods=["POST"])
def create_topic():
    """Create a new topic"""
    data = request.json or {}
    try:
        topic_name = data.get("topic")
        if not topic_name:
            return jsonify({"error": "Topic name is required"}), 400

        topic = TopicService.create_topic(topic=topic_name)
        return jsonify(topic.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating topic: {e}")
        return jsonify({"error": str(e)}), 400


@topics_bp.route("/topics", methods=["GET"])
def get_topics():
    """Get all topics"""
    try:
        topics = Topic.get_all()
        return jsonify([t.to_dict() for t in topics])
    except Exception as e:
        current_app.logger.error(f"Error fetching topics: {e}")
        return jsonify({"error": str(e)}), 400


@topics_bp.route("/topics/<int:topic_id>", methods=["GET"])
def get_topic(topic_id):
    """Get specific topic"""
    try:
        topic = Topic.get_by_id(topic_id)
        if not topic:
            return jsonify({"error": "Topic not found"}), 404
        return jsonify(topic.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error fetching topic: {e}")
        return jsonify({"error": str(e)}), 400


@topics_bp.route("/topics/<int:topic_id>", methods=["PUT"])
def update_topic(topic_id):
    """Update an existing topic"""
    data = request.json or {}
    try:
        topic_name = data.get("topic")
        if not topic_name:
            return jsonify({"error": "Topic name is required"}), 400

        topic = TopicService.update_topic(topic_id=topic_id, topic=topic_name)
        return jsonify(topic.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating topic: {e}")
        return jsonify({"error": str(e)}), 400


@topics_bp.route("/topics/<int:topic_id>", methods=["DELETE"])
def delete_topic(topic_id):
    """Soft delete or deactivate topic"""
    try:
        result = TopicService.delete_topic(topic_id)
        return jsonify({"success": True, "topic_id": topic_id})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting topic: {e}")
        return jsonify({"error": str(e)}), 400
