from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling in-app notifications as mentioned in README"""
    
    def __init__(self):
        self.notifications = []  # In-memory storage for demo
    
    def send_notification(self, user_internal_id: int, message: str, notification_type: str = "info") -> Dict[str, Any]:
        """Send notification to user"""
        notification = {
            "id": len(self.notifications) + 1,
            "user_internal_id": user_internal_id,
            "message": message,
            "type": notification_type,
            "timestamp": "2024-01-01T00:00:00Z",  # Should use datetime.utcnow()
            "read": False
        }
        self.notifications.append(notification)
        logger.info(f"Notification sent to user {user_internal_id}: {message}")
        return notification
    
    def get_user_notifications(self, user_internal_id: int) -> List[Dict[str, Any]]:
        """Get all notifications for a user"""
        return [n for n in self.notifications if n["user_internal_id"] == user_internal_id]
    
    def mark_as_read(self, notification_id: int, user_internal_id: int) -> bool:
        """Mark notification as read"""
        for notification in self.notifications:
            if notification["id"] == notification_id and notification["user_internal_id"] == user_internal_id:
                notification["read"] = True
                return True
        return False

    def notify_list_change(self, list_id: int, change_type: str):
        # Implementation needed
        pass

    def notify_lock_acquired(self, list_id: int, user_id: int):
        logger.info(f"Notification: User {user_id} acquired lock on list {list_id}")

    def notify_lock_released(self, list_id: int, user_id: int):
        logger.info(f"Notification: User {user_id} released lock on list {list_id}")
