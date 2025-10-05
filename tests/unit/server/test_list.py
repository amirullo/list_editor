
import pytest
from unittest.mock import MagicMock
from app.services.list_service import ListService
from app.schemas.list_schema import ListCreate, ListInDB
from app.models.list_model import List
from app.models.global_role_model import GlobalRoleType
from app.models.list_role_model import ListRole, ListRoleType
from app.models.list_user_model import ListUser
from app.repositories.list_repository import ListRepository
from app.repositories.list_user_repository import ListUserRepository
from app.repositories.user_repository import UserRepository
from app.core.db import SessionLocal, engine, Base
# from app.models import user_model, list_model, list_user_model, list_role_model, global_role_model, item_model, lock_model


@pytest.fixture(scope="function")
def test_db():
    # Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Base.metadata.drop_all(bind=engine)


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

    def test_create_list_repo_level_integration(
        self,
        test_db,
        mock_global_role_service: MagicMock,
        mock_list_role_service: MagicMock,
        mock_item_service: MagicMock
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        list_user_repo = ListUserRepository(db=test_db)
        user_repo = UserRepository(db=test_db)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            list_user_repository=list_user_repo,
            user_repository=user_repo,
            global_role_service=mock_global_role_service,
            list_role_service=mock_list_role_service,
            item_service=mock_item_service,
        )

        client_external_id = "client_user"
        worker_external_id = "creator_user"
        list_name = "Test List2"

        # Create data in the test database
        user_client = user_repo.create_if_not_exists(client_external_id, role_type=GlobalRoleType.CLIENT)
        user_worker = user_repo.create_if_not_exists(worker_external_id, role_type=GlobalRoleType.WORKER)

        created_list = list_repo.create({"name": list_name})
        list_id = created_list.id

        list_user_repo.create(user_internal_id=user_client.id, list_id=list_id, role_type=ListRoleType.CREATOR)
        list_user_repo.create(user_internal_id=user_worker.id, list_id=list_id, role_type=ListRoleType.USER)

        # Act
        result = list_service.get_list(list_id=list_id, user_internal_id=user_client.id)

        # Assert
        assert isinstance(result, ListInDB)
        assert result.id == list_id
        assert result.name == list_name
        assert result.creator_id == user_client.id
        assert user_client.id in result.user_id_list
        assert user_worker.id in result.user_id_list

    def test_create_list_service_level_integration(
        self,
        test_db,
        mock_global_role_service: MagicMock,
        mock_list_role_service: MagicMock,
        mock_item_service: MagicMock
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        list_user_repo = ListUserRepository(db=test_db)
        user_repo = UserRepository(db=test_db)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            list_user_repository=list_user_repo,
            user_repository=user_repo,
            global_role_service=mock_global_role_service,
            list_role_service=mock_list_role_service,
            item_service=mock_item_service,
        )

        list_name = "Test List3"
        client_external_id = "client_user" # existing user CLIENT
        worker_external_id = "creator_user" # existing user WORKER
        external_id_list = [client_external_id, worker_external_id]

        # Act
        results = []
        for external_id in external_id_list:
            user = user_repo.create_if_not_exists(external_id)
            list_create_data = ListCreate(name=list_name)
            create_result = list_service.create_list(list_create=list_create_data,
                                                     user_external_id=external_id
                                                     )
            get_result = list_service.get_list(list_id=create_result.id,
                                               user_internal_id=user.id
                                               )
            results.append((user, create_result, get_result))

        # Assert
        for user, create_result, get_result in results:
            assert isinstance(create_result, ListInDB)
            assert create_result.id == get_result.id
            assert get_result.name == list_name
            assert get_result.creator_id == user.id
            assert user.id in get_result.user_id_list


