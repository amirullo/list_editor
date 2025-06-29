from fastapi import HTTPException, status

class ListNotFoundException(HTTPException):
    def __init__(self, detail="List not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class LockException(HTTPException):
    def __init__(self, detail="List is locked by another user"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class PermissionException(HTTPException):
    def __init__(self, detail="You don't have permission to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)