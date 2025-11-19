import pytest
from app.services.list_service import ListService
from app.schemas.list_schema import ListCreate, ListInDB
from app.repositories.list_repository import ListRepository
from app.repositories.user_repository import UserRepository
from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService
from app.core.db import SessionLocal
from app.schemas.user_schema import UserCreate
from app.schemas.project_schema import ProjectCreate
import uuid


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
        user_repo = UserRepository(db=test_db)
        project_repo = ProjectRepository(db=test_db)
        project_service = ProjectService(db=test_db)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            project_repository=project_repo,
            item_service=None, # Not used in this test
        )

        client_external_id = str(uuid.uuid4())
        worker_external_id = str(uuid.uuid4())
        list_name = "Test Get List"
        destination_address = "123 Main St, Anytown"
        project_name = "Test Project for List"

        # Create users
        user_client = user_repo.get_by_external_id(client_external_id)
        if not user_client:
            user_client = user_repo.create(user_create=UserCreate(external_id=client_external_id))
        
        user_worker = user_repo.get_by_external_id(worker_external_id)
        if not user_worker:
            user_worker = user_repo.create(user_create=UserCreate(external_id=worker_external_id))

        # Create project with client as creator
        project_create_data = ProjectCreate(name=project_name)
        created_project = project_service.create_project(project_create_data, user_client.id)
        project_id = created_project.id

        # Add worker to the project
        project_service.add_user_to_project(project_id, worker_external_id, user_client.id)

        # Use list_service to create the list within the project
        list_create_data = ListCreate(name=list_name, destination_address=destination_address, project_id=project_id)
        created_list = list_service.create_list(list_create=list_create_data, user_internal_id=user_client.id)
        list_id = created_list.id

        # Act
        result = list_service.get_list(list_id=list_id, user_internal_id=user_client.id)

        # Assert
        assert isinstance(result, ListInDB)
        assert result.id == list_id
        assert result.name == list_name
        assert result.destination_address == destination_address
        assert result.project_id == project_id

        # Verify worker can also access the list (inherits from project)
        worker_access_result = list_service.get_list(list_id=list_id, user_internal_id=user_worker.id)
        assert worker_access_result.id == list_id

    def test_create_list_service_level_integration(
        self,
        test_db
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        user_repo = UserRepository(db=test_db)
        project_repo = ProjectRepository(db=test_db)
        project_service = ProjectService(db=test_db)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            project_repository=project_repo,
            item_service=None, # Not used in this test
        )

        list_name = "Test Create List Service"
        destination_address = "456 Oak Ave, Otherville"
        project_name = "Test Project for Create List"
        external_id = str(uuid.uuid4())

        # Create user
        user = user_repo.get_by_external_id(external_id)
        if not user:
            user = user_repo.create(user_create=UserCreate(external_id=external_id))
        
        # Create project
        project_create_data = ProjectCreate(name=project_name)
        created_project = project_service.create_project(project_create_data, user.id)
        project_id = created_project.id

        # Act
        list_create_data = ListCreate(name=list_name, destination_address=destination_address, project_id=project_id)
        create_result = list_service.create_list(list_create=list_create_data, user_internal_id=user.id)
        
        get_result = list_service.get_list(list_id=create_result.id, user_internal_id=user.id)

        # Assert
        assert isinstance(create_result, ListInDB)
        assert create_result.id == get_result.id
        assert get_result.name == list_name
        assert get_result.destination_address == destination_address
        assert get_result.project_id == project_id

    @pytest.mark.asyncio
    async def test_get_all_lists_for_project_integration(
            self,
            test_db
    ):
        # Arrange
        list_repo = ListRepository(db=test_db)
        user_repo = UserRepository(db=test_db)
        project_repo = ProjectRepository(db=test_db)
        project_service = ProjectService(db=test_db)

        list_service = ListService(
            db=test_db,
            list_repository=list_repo,
            project_repository=project_repo,
            item_service=None,  # Not used in this test
        )

        destination_address1 = "222 Maple Ave, Townsville"
        destination_address2 = "333 Birch Ln, Cityburg"
        creator_external_id = str(uuid.uuid4())
        
        # Create user
        creator = user_repo.get_by_external_id(creator_external_id)
        if not creator:
            creator = user_repo.create(user_create=UserCreate(external_id=creator_external_id))

        # Create project
        project_create_data = ProjectCreate(name="Project for All Lists Test")
        created_project = project_service.create_project(project_create_data, creator.id)
        project_id = created_project.id

        # Create lists within the project
        list_create_data1 = ListCreate(name="List One", destination_address=destination_address1, project_id=project_id)
        created_list1 = list_service.create_list(list_create=list_create_data1, user_internal_id=creator.id)

        list_create_data2 = ListCreate(name="List Two", destination_address=destination_address2, project_id=project_id)
        created_list2 = list_service.create_list(list_create=list_create_data2, user_internal_id=creator.id)

        # Act
        result = list_service.get_all_lists_for_project(project_id=project_id, user_internal_id=creator.id)
        
        # Assert
        assert len(result) == 2
        for mylist in result:
            assert isinstance(mylist, ListInDB)
            if mylist.id == created_list1.id:
                assert mylist.destination_address == destination_address1
            elif mylist.id == created_list2.id:
                assert mylist.destination_address == destination_address2
        assert created_list1.id in [x.id for x in result]
        assert created_list2.id in [x.id for x in result]
