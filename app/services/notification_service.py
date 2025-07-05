from typing import List, Dict

class NotificationService:
    _notifications = []  # Class variable to store notifications across all instances

    def __init__(self):
        # We can keep the __init__ method for potential future instance-specific initializations
        pass

    def send_notification(self, message: str) -> None:
        """
        Sends an in-app notification with the given message
        """
        self.__class__._notifications.append(message)

    def get_notifications(self) -> List[str]:
        """
        Retrieves all notifications
        """
        return self.__class__._notifications