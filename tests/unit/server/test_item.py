import pytest
from unittest.mock import Mock
from datetime import datetime
from app.services.item_service import ItemService
from app.schemas.item_schema import ItemCreate, ItemInDB
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.item_model import Item
from app.models.list_model import List

@pytest.fixture
def mock_item_repository():
    return Mock()

@pytest.fixture
def mock_list_repository():
    return Mock()

@pytest.fixture
def mock_global_role_service():
    return Mock()

@pytest.fixture
def mock_list_role_service():
    return Mock()

@pytest.fixture
def item_service(mock_item_repository, mock_list_repository, mock_global_role_service, mock_list_role_service):
    return ItemService(
        db=Mock(),
        item_repository=mock_item_repository,
        list_repository=mock_list_repository,
        global_role_service=mock_global_role_service,
        list_role_service=mock_list_role_service
    )

def test_create_item_successfully(item_service, mock_item_repository, mock_list_repository, mock_list_role_service):
    # Arrange
    list_id = 1
    user_internal_id = 1
    item_create = ItemCreate(name="Test Item", description="A test item")
    
    mock_list_role_service.user_has_access_to_list.return_value = True
    mock_list_repository.get_by_id.return_value = List(id=list_id, name="Test List")
    
    current_time = datetime.now()
    mock_item_repository.create.return_value = Item(
        id=1,
        list_id=list_id,
        name=item_create.name,
        description=item_create.description,
        quantity=1,
        created_at=current_time,
        updated_at=current_time,
        approved=0,
        bought=0,
        delivered=0,
    )

    # Act
    created_item = item_service.create_item(list_id, item_create, user_internal_id)

    # Assert
    mock_list_role_service.user_has_access_to_list.assert_called_once_with(user_internal_id, list_id)
    mock_list_repository.get_by_id.assert_called_once_with(list_id)
    mock_item_repository.create.assert_called_once_with(list_id, item_create.model_dump(exclude_unset=True))
    
    assert isinstance(created_item, ItemInDB)
    assert created_item.name == item_create.name
    assert created_item.description == item_create.description
    assert created_item.list_id == list_id
    assert created_item.quantity == 1
    assert created_item.created_at == current_time
    assert created_item.updated_at == current_time
    assert created_item.approved == 0
    assert created_item.bought == 0
    assert created_item.delivered == 0

def test_create_item_no_access_to_list(item_service, mock_list_role_service):
    # Arrange
    list_id = 1
    user_internal_id = 1
    item_create = ItemCreate(name="Test Item", description="A test item")
    
    mock_list_role_service.user_has_access_to_list.return_value = False

    # Act & Assert
    with pytest.raises(ForbiddenException, match="No access to this list"):
        item_service.create_item(list_id, item_create, user_internal_id)
    
    mock_list_role_service.user_has_access_to_list.assert_called_once_with(user_internal_id, list_id)

def test_create_item_list_not_found(item_service, mock_list_repository, mock_list_role_service):
    # Arrange
    list_id = 1
    user_internal_id = 1
    item_create = ItemCreate(name="Test Item", description="A test item")
    
    mock_list_role_service.user_has_access_to_list.return_value = True
    mock_list_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundException, match="List not found"):
        item_service.create_item(list_id, item_create, user_internal_id)
    
    mock_list_role_service.user_has_access_to_list.assert_called_once_with(user_internal_id, list_id)

def test_get_item_successfully(item_service, mock_item_repository, mock_list_role_service):
    # Arrange
    list_id = 1
    item_id = 1
    user_internal_id = 1
    current_time = datetime.now()
    expected_item = Item(
        id=item_id,
        list_id=list_id,
        name="Retrieved Item",
        description="Description of retrieved item",
        quantity=1,
        created_at=current_time,
        updated_at=current_time,
        approved=0,
        bought=0,
        delivered=0
    )
    
    mock_list_role_service.user_has_access_to_list.return_value = True
    mock_item_repository.get_by_id.return_value = expected_item

    # Act
    retrieved_item = item_service.get_item(list_id, item_id, user_internal_id)

    # Assert
    mock_list_role_service.user_has_access_to_list.assert_called_once_with(user_internal_id, list_id)
    mock_item_repository.get_by_id.assert_called_once_with(list_id, item_id)
    
    assert isinstance(retrieved_item, ItemInDB)
    assert retrieved_item.id == expected_item.id
    assert retrieved_item.name == expected_item.name
    assert retrieved_item.description == expected_item.description
    assert retrieved_item.list_id == expected_item.list_id
    assert retrieved_item.quantity == 1
    assert retrieved_item.approved == 0
    assert retrieved_item.bought == 0
    assert retrieved_item.delivered == 0

def test_get_item_no_access_to_list(item_service, mock_list_role_service):
    # Arrange
    list_id = 1
    item_id = 1
    user_internal_id = 1
    
    mock_list_role_service.user_has_access_to_list.return_value = False

    # Act & Assert
    with pytest.raises(ForbiddenException, match="No access to this list"):
        item_service.get_item(list_id, item_id, user_internal_id)
    
    mock_list_role_service.user_has_access_to_list.assert_called_once_with(user_internal_id, list_id)

def test_get_item_not_found(item_service, mock_item_repository, mock_list_role_service):
    # Arrange
    list_id = 1
    item_id = 1
    user_internal_id = 1
    
    mock_list_role_service.user_has_access_to_list.return_value = True
    mock_item_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundException, match="Item not found"):
        item_service.get_item(list_id, item_id, user_internal_id)
    
    mock_list_role_service.user_has_access_to_list.assert_called_once_with(user_internal_id, list_id)
    mock_item_repository.get_by_id.assert_called_once_with(list_id, item_id)