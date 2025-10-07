from app.models.segment import Segment
from app.models.user import User

class SegmentService:
    @staticmethod
    def create_segment(name, definition):
        '''Create a new segment'''
        segment = Segment(segment=name, definition=definition)  # Changed parameter name
        return segment.save()

    @staticmethod
    def evaluate_segment_members(segment_id):
        '''Evaluate and return segment members'''
        segment = Segment.get_by_id(segment_id)
        if not segment:
            raise ValueError("Segment not found")
        
        definition = segment.definition
        filters = definition.get('filters', [])
        all_users = User.get_all()
        matched_users = []
        
        for user in all_users:
            if SegmentService._user_matches_filters(user, filters):
                matched_users.append(user)
        
        return matched_users
    
    @staticmethod
    def _user_matches_filters(user, filters):
        '''Check if user matches all segment filters'''
        for filter_obj in filters:
            path = filter_obj.get('path', '')
            if not path.startswith('attributes.'):
                return False
            
            key = path.split('.', 1)[1]
            op = filter_obj.get('op', 'eq')
            value = filter_obj.get('value')
            
            if op == 'eq':
                if user.attributes.get(key) != value:
                    return False
            else:
                # Add more operators as needed
                return False
        
        return True