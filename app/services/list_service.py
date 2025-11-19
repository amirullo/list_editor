
from typing import List as TypeList, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.list_schema import ListCreate, ListUpdate, ListInDB
from app.schemas.item_schema import ItemCreate
from app.core.exceptions import NotFoundException, LockException, ForbiddenException
from app.utils.logger import logger

class ListService:
    def __init__(
        self, 
        db: Session,
        list_repository: ListRepository, 
        project_repository: ProjectRepository,
        item_service: ItemRepository
    ):
        self.db = db
        self.list_repository = list_repository
        self.project_repository = project_repository
        self.item_service = item_service

    def create_list(self, list_create: ListCreate, user_internal_id: int, items: Optional[TypeList[ItemCreate]] = None) -> ListInDB:
        project = self.project_repository.get_by_id_for_user(list_create.project_id, user_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")

        list_data = list_create.model_dump(exclude_unset=True)
        new_list = self.list_repository.create(list_data)
        if not new_list:
            raise Exception("Failed to create list")
        
        created_items = []
        if items:
            for item_create in items:
                created_item = self.item_service.create_item(new_list.id, item_create, user_internal_id)
                created_items.append(created_item)
        
        response_data = {
            'id': new_list.id,
            'name': new_list.name,
            'project_id': new_list.project_id,
            'created_at': new_list.created_at,
            'updated_at': new_list.updated_at,
            'destination_address': new_list.destination_address,
            'items': created_items
        }
        
        return ListInDB.model_validate(response_data)

    def get_all_lists_for_project(self, project_id: int, user_internal_id: int) -> TypeList[ListInDB]:
        project = self.project_repository.get_by_id_for_user(project_id, user_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")

        db_lists = self.list_repository.get_all_for_project(project_id)
        
        response_lists = []
        for db_list in db_lists:
            response_data = {
                'id': db_list.id,
                'name': db_list.name,
                'project_id': db_list.project_id,
                'created_at': db_list.created_at,
                'updated_at': db_list.updated_at,
                'destination_address': db_list.destination_address,
                'items': db_list.items
            }
            response_lists.append(ListInDB.model_validate(response_data))

        return response_lists

    def get_list(self, list_id: int, user_internal_id: int) -> ListInDB:
        db_list = self.list_repository.get_by_id_for_user(list_id, user_internal_id)
        if not db_list:
            raise NotFoundException("List not found or you don't have access")

        response_data = {
            'id': db_list.id,
            'name': db_list.name,
            'project_id': db_list.project_id,
            'created_at': db_list.created_at,
            'updated_at': db_list.updated_at,
            'destination_address': db_list.destination_address,
            'items': db_list.items
        }
        
        return ListInDB.model_validate(response_data)

    def update_list(self, list_id: int, list_update: ListUpdate, user_internal_id: int) -> ListInDB:
        db_list = self.list_repository.get_by_id_for_user(list_id, user_internal_id)
        if not db_list:
            raise ForbiddenException("You don't have access to this list")
        
        from app.services.lock_service import LockService
        lock_service = LockService(self.db)
        if not lock_service.check_lock(list_id, user_internal_id):
            raise LockException("List is locked by another user")
        
        update_data = list_update.model_dump(exclude_unset=True)
        updated_list = self.list_repository.update(list_id, update_data)
        
        if not updated_list:
            raise NotFoundException("List not found")
        
        return ListInDB.model_validate(updated_list)

    def delete_list(self, list_id: int, user_internal_id: int) -> Dict[str, str]:
        db_list = self.list_repository.get_by_id_for_user(list_id, user_internal_id)
        if not db_list:
            raise ForbiddenException("You don't have access to this list")
        
        success = self.list_repository.delete(list_id)
        if not success:
            raise NotFoundException("List not found")
        
        return {"message": "List deleted successfully", "list_id": str(list_id)}
