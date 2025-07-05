from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class LockException(HTTPException):
    def __init__(self, detail: str = "The resource is locked"):
        super().__init__(status_code=status.HTTP_423_LOCKED, detail=detail)

class PermissionException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

# Add any other custom exceptions here