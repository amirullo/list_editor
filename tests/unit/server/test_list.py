
import pytest
from unittest.mock import MagicMock
from app.services.list_service import ListService
from app.schemas.list_schema import ListCreate, ListInDB
from app.models.list_model import List
from app.models.list_role_model import ListRole, ListRoleType
from app.models.list_user_model import ListUser

@pytest.fixture
def mock_db_session() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_list_repo() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_list_user_repo() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_user_repo() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_global_role_service() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_list_role_service() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_item_service() -> MagicMock:
    return MagicMock()

@pytest.fixture
def list_service(
    mock_db_session: MagicMock,
    mock_list_repo: MagicMock,
    mock_list_user_repo: MagicMock,
    mock_user_repo: MagicMock,
    mock_global_role_service: MagicMock,
    mock_list_role_service: MagicMock,
    mock_item_service: MagicMock,
) -> ListService:
    return ListService(
        db=mock_db_session,
        list_repository=mock_list_repo,
        list_user_repository=mock_list_user_repo,
        user_repository=mock_user_repo,
        global_role_service=mock_global_role_service,
        list_role_service=mock_list_role_service,
        item_service=mock_item_service,
    )

class TestListService:
    def test_create_list_without_items_success(self, list_service: ListService, mock_list_repo: MagicMock, mock_list_user_repo: MagicMock, mock_user_repo: MagicMock, mock_item_service: MagicMock):
        # Arrange
        user_id = "creator_user_id"
        list_create_data = ListCreate(name="New Test List")
        
        mock_new_list = List(id=1, name="New Test List", created_at="2024-01-01T00:00:00", updated_at="2024-01-01T00:00:00")
        mock_list_repo.create.return_value = mock_new_list
        
        # When get_users_by_list_id is called after creation, it should return the creator
        mock_list_user_repo.get_users_by_list_id.return_value = [
            ListUser(user_id=user_id, list_id=1, role=ListRole(role_type=ListRoleType.CREATOR))
        ]

        # Act
        result = list_service.create_list(list_create=list_create_data, user_id=user_id, items=None)

        # Assert
        mock_user_repo.create_if_not_exists.assert_called_once_with(user_id)
        mock_list_repo.create.assert_called_once_with(list_create_data.model_dump(exclude_unset=True))
        mock_list_user_repo.create.assert_called_once_with(
            user_id=user_id,
            list_id=mock_new_list.id,
            role_type=ListRoleType.CREATOR
        )
        mock_list_user_repo.get_users_by_list_id.assert_called_once_with(mock_new_list.id)
        mock_item_service.create_item.assert_not_called()

        assert isinstance(result, ListInDB)
        assert result.id == mock_new_list.id
        assert result.name == list_create_data.name
        assert result.creator_id == user_id
        assert user_id in result.user_id_list
        assert len(result.user_id_list) == 1
