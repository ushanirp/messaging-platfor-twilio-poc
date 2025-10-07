from flask import Blueprint, request, jsonify, current_app
from app.models.subscription import Subscription
from app.services.subscription_service import SubscriptionService

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route("/subscriptions", methods=["POST"])
def create_subscription():
    """Create a new user subscription to a topic"""
    data = request.json or {}
    try:
        subscription = SubscriptionService.create_subscription(
            phone_number=data.get("phone_number"),
            topic_id=data.get("topic_id")
        )
        return jsonify(subscription.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating subscription: {e}")
        return jsonify({"error": str(e)}), 400


@subscriptions_bp.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    """Get all subscriptions"""
    subscriptions = Subscription.get_all()
    return jsonify([s.to_dict() for s in subscriptions])


@subscriptions_bp.route("/subscriptions/<int:sub_id>", methods=["GET"])
def get_subscription(sub_id):
    """Get a specific subscription"""
    subscription = Subscription.get_by_id(sub_id)
    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404
    return jsonify(subscription.to_dict())


@subscriptions_bp.route("/subscriptions/<int:sub_id>", methods=["PUT"])
def update_subscription(sub_id):
    """Update subscription details"""
    data = request.json or {}
    try:
        sub = SubscriptionService.update_subscription(
            sub_id=sub_id,
            consent_state=data.get("consent_state"),
            is_active=data.get("is_active")
        )
        return jsonify(sub.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating subscription: {e}")
        return jsonify({"error": str(e)}), 400


@subscriptions_bp.route("/subscriptions/<int:sub_id>", methods=["DELETE"])
def delete_subscription(sub_id):
    """Deactivate or delete a subscription"""
    try:
        result = SubscriptionService.delete_subscription(sub_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting subscription: {e}")
        return jsonify({"error": str(e)}), 400
