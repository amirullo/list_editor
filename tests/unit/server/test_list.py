
import pytest
from app.services.list_service import ListService
from app.schemas.list_schema import ListCreate, ListInDB
from app.models.list_role_model import ListRoleType
from app.repositories.list_repository import ListRepository
from app.repositories.list_user_repository import ListUserRepository
from app.repositories.user_repository import UserRepository
from app.repositories.global_role_repository import GlobalRoleRepository
from app.services.global_role_service import GlobalRoleService
from app.core.db import SessionLocal
from app.services.list_role_service import ListRoleService
from app.services.user_service import UserService


@pytest.fixture(scope="function")
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestListService:

    @pytest.mark.asyncio
    async def test_get_list_integration(
        self,
        test_db
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        list_user_repo = ListUserRepository(db=test_db)
        user_repo = UserRepository(db=test_db)
        global_role_repo = GlobalRoleRepository(db=test_db)
        global_role_service = GlobalRoleService(global_role_repository=global_role_repo)
        list_role_service = ListRoleService(list_user_repository=list_user_repo)
        user_service = UserService(user_repository=user_repo)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            list_user_repository=list_user_repo,
            user_repository=user_repo,
            global_role_service=global_role_service,
            list_role_service=list_role_service,
            item_service=None, # Not used in this test
        )

        client_external_id = "client_user_get"
        worker_external_id = "worker_user_get"
        list_name = "Test Get List"

        # Create data in the test database
        user_client = user_service.get_user_by_external_id(client_external_id)
        if not user_client:
            user_client = user_service.create_user(external_id=client_external_id)
        
        user_worker = user_service.get_user_by_external_id(worker_external_id)
        if not user_worker:
            user_worker = user_service.create_user(external_id=worker_external_id)

        global_role_service.assign_client_role(user_client.id)
        global_role_service.assign_worker_role(user_worker.id)

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
        assert list_role_service.is_user_list_creator(user_id=user_client.id, list_id=list_id)
        assert list_role_service.user_has_access_to_list(user_id=user_client.id, list_id=list_id)
        assert list_role_service.user_has_access_to_list(user_id=user_worker.id, list_id=list_id)
        assert list_role_service.get_user_role_in_list(user_id=user_client.id, list_id=list_id) == ListRoleType.CREATOR
        assert list_role_service.get_user_role_in_list(user_id=user_worker.id, list_id=list_id) == ListRoleType.USER

    def test_create_list_service_level_integration(
        self,
        test_db
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        list_user_repo = ListUserRepository(db=test_db)
        user_repo = UserRepository(db=test_db)
        global_role_repo = GlobalRoleRepository(db=test_db)
        global_role_service = GlobalRoleService(global_role_repository=global_role_repo)
        user_service = UserService(user_repository=user_repo)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            list_user_repository=list_user_repo,
            user_repository=user_repo,
            global_role_service=global_role_service,
            list_role_service=None, # Not used in this test
            item_service=None, # Not used in this test
        )

        list_name = "Test Create List Service"
        external_id = "creator_user_create"

        # Act
        user = user_service.get_user_by_external_id(external_id)
        if not user:
            user = user_service.create_user(external_id=external_id)
        global_role_service.assign_client_role(user.id)
        list_create_data = ListCreate(name=list_name)
        create_result = list_service.create_list(list_create=list_create_data,
                                                 user_internal_id=user.id
                                                 )
        get_result = list_service.get_list(list_id=create_result.id,
                                           user_internal_id=user.id
                                           )

        # Assert
        assert isinstance(create_result, ListInDB)
        assert create_result.id == get_result.id
        assert get_result.name == list_name
        assert get_result.creator_id == user.id
        assert user.id in get_result.user_id_list

    def test_adding_user_to_list_service_level_integration(
        self,
        test_db
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        list_user_repo = ListUserRepository(db=test_db)
        user_repo = UserRepository(db=test_db)
        global_role_repo = GlobalRoleRepository(db=test_db)
        global_role_service = GlobalRoleService(global_role_repository=global_role_repo)
        list_role_service = ListRoleService(list_user_repository=list_user_repo)
        user_service = UserService(user_repository=user_repo)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            list_user_repository=list_user_repo,
            user_repository=user_repo,
            global_role_service=global_role_service,
            list_role_service=list_role_service,
            item_service=None, # Not used in this test
        )

        list_name = "Test Add User To List"
        creator_external_id = "creator_for_add_user_test"
        user_to_add_external_id = "user_to_add_test"

        # Create users
        creator = user_service.get_user_by_external_id(creator_external_id)
        if not creator:
            creator = user_service.create_user(external_id=creator_external_id)
        user_to_add = user_service.get_user_by_external_id(user_to_add_external_id)
        if not user_to_add:
            user_to_add = user_service.create_user(external_id=user_to_add_external_id)

        # Create list
        list_create_data = ListCreate(name=list_name)
        created_list = list_service.create_list(list_create=list_create_data,
                                                 user_internal_id=creator.id
                                                 )

        # Act
        updated_list = list_service.add_user_to_list(list_id=created_list.id,
                                                     user_internal_id_to_add=user_to_add.id,
                                                     requester_internal_id=creator.id
                                                     )

        # Assert
        assert isinstance(updated_list, ListInDB)
        assert created_list.id == updated_list.id
        assert user_to_add.id in updated_list.user_id_list
        assert creator.id in updated_list.user_id_list

    def test_removing_user_from_list_service_level_integration(
        self,
        test_db
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        list_user_repo = ListUserRepository(db=test_db)
        user_repo = UserRepository(db=test_db)
        global_role_repo = GlobalRoleRepository(db=test_db)
        global_role_service = GlobalRoleService(global_role_repository=global_role_repo)
        list_role_service = ListRoleService(list_user_repository=list_user_repo)
        user_service = UserService(user_repository=user_repo)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            list_user_repository=list_user_repo,
            user_repository=user_repo,
            global_role_service=global_role_service,
            list_role_service=list_role_service,
            item_service=None, # Not used in this test
        )

        list_name = "Test Remove User From List"
        creator_external_id = "creator_for_remove_user_test"
        user_to_remove_external_id = "user_to_remove_test"

        # Create users
        creator = user_service.get_user_by_external_id(creator_external_id)
        if not creator:
            creator = user_service.create_user(external_id=creator_external_id)
        user_to_remove = user_service.get_user_by_external_id(user_to_remove_external_id)
        if not user_to_remove:
            user_to_remove = user_service.create_user(external_id=user_to_remove_external_id)

        # Create list
        list_create_data = ListCreate(name=list_name)
        created_list = list_service.create_list(list_create=list_create_data,
                                                 user_internal_id=creator.id
                                                 )
        
        # Add user to the list first
        list_service.add_user_to_list(list_id=created_list.id,
                                      user_internal_id_to_add=user_to_remove.id,
                                      requester_internal_id=creator.id
                                      )

        # Act
        updated_list = list_service.remove_user_from_list(list_id=created_list.id,
                                                          user_internal_id_to_remove=user_to_remove.id,
                                                          requester_internal_id=creator.id
                                                          )

        # Assert
        assert isinstance(updated_list, ListInDB)
        assert created_list.id == updated_list.id
        assert user_to_remove.id not in updated_list.user_id_list
        assert creator.id in updated_list.user_id_list

    @pytest.mark.asyncio
    async def test_get_all_lists_integration(
            self,
            test_db
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        list_user_repo = ListUserRepository(db=test_db)
        user_repo = UserRepository(db=test_db)
        global_role_repo = GlobalRoleRepository(db=test_db)
        global_role_service = GlobalRoleService(global_role_repository=global_role_repo)
        list_role_service = ListRoleService(list_user_repository=list_user_repo)
        user_service = UserService(user_repository=user_repo)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            list_user_repository=list_user_repo,
            user_repository=user_repo,
            global_role_service=global_role_service,
            list_role_service=list_role_service,
            item_service=None,  # Not used in this test
        )

        list_name = "Test Add User To List"
        creator_external_id = "creator_for_add_user_test222"
        user_to_add_external_id = "user_to_add_test222"

        # Create users
        creator = user_service.get_user_by_external_id(creator_external_id)
        if not creator:
            creator = user_service.create_user(external_id=creator_external_id)
        user_to_add = user_service.get_user_by_external_id(user_to_add_external_id)
        if not user_to_add:
            user_to_add = user_service.create_user(external_id=user_to_add_external_id)

        global_role_service.assign_client_role(creator.id)
        global_role_service.assign_worker_role(user_to_add.id)

        # Create list
        list_create_data = ListCreate(name=list_name)
        created_list1 = list_service.create_list(list_create=list_create_data,
                                                user_internal_id=creator.id
                                                )

        list_create_data = ListCreate(name=list_name)
        created_list2 = list_service.create_list(list_create=list_create_data,
                                                user_internal_id=user_to_add.id
                                                )

        # Act
        updated_list = list_service.add_user_to_list(list_id=created_list1.id,
                                                     user_internal_id_to_add=user_to_add.id,
                                                     requester_internal_id=creator.id
                                                     )

        # Act

        result = list_service.get_all_lists(user_internal_id=user_to_add.id)
        result
