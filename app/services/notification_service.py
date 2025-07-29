from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling in-app notifications as mentioned in README"""
    
    def __init__(self):
        self.notifications = []  # In-memory storage for demo
    
    def send_notification(self, user_id: str, message: str, notification_type: str = "info") -> Dict[str, Any]:
        """Send notification to user"""
        notification = {
            "id": len(self.notifications) + 1,
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "timestamp": "2024-01-01T00:00:00Z",  # Should use datetime.utcnow()
            "read": False
        }
        self.notifications.append(notification)
        logger.info(f"Notification sent to user {user_id}: {message}")
        return notification
    
    def get_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all notifications for a user"""
        return [n for n in self.notifications if n["user_id"] == user_id]
    
    def mark_as_read(self, notification_id: int, user_id: str) -> bool:
        """Mark notification as read"""
        for notification in self.notifications:
            if notification["id"] == notification_id and notification["user_id"] == user_id:
                notification["read"] = True
                return True
        return False

    def notify_list_change(self, list_id: int, change_type: str):
        # Implementation needed
        pass