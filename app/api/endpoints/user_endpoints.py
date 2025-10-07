
from fastapi import APIRouter, Depends
from app.api.dependencies import get_user_repository, get_external_user_id
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserResponse
from app.models.user_model import User

router = APIRouter()


@router.post("/login", response_model=UserResponse)
def login_or_create_user(
    user_external_id: str = Depends(get_external_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Logs in a user with an external ID from the 'X-User-ID' header.
    If the user does not exist, a new user is created.
    Returns the user's internal and external IDs.
    """
    user = user_repo.get_or_create_by_external_id(user_external_id)
    return user
