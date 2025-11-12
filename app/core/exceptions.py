
from fastapi import status

class BaseAPIException(Exception):
    """Base class for all API exceptions."""
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)

class NotFoundException(BaseAPIException):
    """Raised when a requested resource is not found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)

class PermissionException(BaseAPIException):
    """Raised when a user does not have permission to perform an action."""
    def __init__(self, detail: str = "Permission denied", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class ForbiddenException(PermissionException):
    """A more specific permission-related exception for forbidden access."""
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)

class LockException(BaseAPIException):
    """Raised for errors related to locking or unlocking resources."""
    def __init__(self, detail: str = "Lock operation failed"):
        super().__init__(detail, status.HTTP_409_CONFLICT)

class ConflictException(BaseAPIException):
    def __init__(self, detail: str = "User is already in this list"):
        super().__init__(detail, status.HTTP_409_CONFLICT)

class BadRequestException(BaseAPIException):
    """Raised for malformed or invalid client requests."""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


