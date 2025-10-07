from app.models.subscription import Subscription

class SubscriptionService:

    @staticmethod
    def create_subscription(phone_number, topic_id):
        """Create a new subscription"""
        return Subscription.create(phone_number, topic_id)

    @staticmethod
    def get_subscriptions_by_user(phone_number):
        return Subscription.get_by_phone(phone_number)

    @staticmethod
    def get_subscriptions_by_topic(topic_id):
        return Subscription.get_by_topic(topic_id)

    @staticmethod
    def delete_subscription(phone_number, topic_id):
        return Subscription.delete(phone_number, topic_id)