from app.models.topic import Topic

class TopicService:
    @staticmethod
    def create_topic(topic):
        return Topic.create(topic)

    @staticmethod
    def list_topics(active_only=True):
        return Topic.get_all(active_only=active_only)

    @staticmethod
    def deactivate_topic(topic_id):
        Topic.deactivate(topic_id)
