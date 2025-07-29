class BaseAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(BaseAPIException):
    """Exception raised when a resource is not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

class ForbiddenException(BaseAPIException):
    """Exception raised when access is forbidden"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, 403)

class LockException(BaseAPIException):
    """Exception raised when lock operations fail"""
    def __init__(self, message: str = "Lock operation failed"):
        super().__init__(message, 409)

class PermissionException(BaseAPIException):
    """Exception raised when user lacks required permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)