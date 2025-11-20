
from fastapi import APIRouter, Depends
from app.api.dependencies import get_external_user_id, get_user_service
from app.services.user_service import UserService
from app.schemas.user_schema import UserResponse
from app.models.user_model import User
from app.utils.logger import logger

router = APIRouter()


@router.post("/login", response_model=UserResponse)
def login_or_create_user(
    user_external_id: str = Depends(get_external_user_id),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse: # Changed return type hint to UserResponse
    """
    Logs in a user with an external ID from the 'X-User-ID' header.
    If the user does not exist, a new user is created.
    Returns the user's internal and external IDs.
    """
    user = user_service.get_or_create_user_by_external_id(user_external_id)
    logger.info(f"User internal_id type: {type(user.internal_id)}, value: {user.internal_id}")
    return UserResponse(external_id=user.external_id, internal_id=user.internal_id)
