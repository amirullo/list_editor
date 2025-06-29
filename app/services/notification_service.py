from typing import List, Dict

class NotificationService:
    def __init__(self):
        # In a real application, this might be a database or a queue
        self.notifications = []
    
    def send_notification(self, message: str) -> None:
        """
        Sends an in-app notification with the given message
        """
        self.notifications.append(message)
    
    def get_notifications(self) -> List[str]:
        """
        Returns all notifications and clears the queue
        """
        notifications = self.notifications.copy()
        self.notifications = []
        return notifications