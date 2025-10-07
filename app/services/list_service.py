
from typing import List as TypeList, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.list_user_repository import ListUserRepository
from app.repositories.user_repository import UserRepository
from app.models.list_role_model import ListRoleType
from app.models.global_role_model import GlobalRoleType
from app.schemas.list_schema import ListCreate, ListUpdate, ListInDB
from app.schemas.item_schema import ItemCreate
from app.core.exceptions import NotFoundException, LockException, ForbiddenException, PermissionException
from app.utils.logger import logger


class ListService:
    def __init__(
        self, 
        db: Session,
        list_repository: ListRepository, 
        list_user_repository: ListUserRepository,
        user_repository: UserRepository,
        global_role_service: Any,
        list_role_service: Any,
        item_service: ItemRepository
    ):
        self.db = db
        self.list_repository = list_repository
        self.list_user_repository = list_user_repository
        self.user_repository = user_repository
        self.global_role_service = global_role_service
        self.list_role_service = list_role_service
        self.item_service = item_service

    def create_list(self, list_create: ListCreate, user_internal_id: int, items: Optional[TypeList[ItemCreate]] = None) -> ListInDB:
        list_data = list_create.model_dump(exclude_unset=True)
        new_list = self.list_repository.create(list_data)
        if not new_list:
            raise Exception("Failed to create list")
        
        self.list_user_repository.create(
            user_internal_id=user_internal_id,
            list_id=new_list.id,
            role_type=ListRoleType.CREATOR
        )
        
        created_items = []
        if items:
            for item_create in items:
                created_item = self.item_service.create_item(new_list.id, item_create, user_internal_id)
                created_items.append(created_item)
        
        list_users = self.list_user_repository.get_users_by_list_id(new_list.id)
        user_id_list = [lu.user_id for lu in list_users]
        
        creator_id = user_internal_id
        if creator_id not in user_id_list:
            user_id_list.append(creator_id)
        
        response_data = {
            'id': new_list.id,
            'name': new_list.name,
            'creator_id': creator_id,
            'user_id_list': user_id_list,
            'created_at': new_list.created_at,
            'updated_at': new_list.updated_at,
            'items': created_items
        }
        
        logger.info(f"Created list {new_list.id} with creator {user_internal_id}")
        return ListInDB.model_validate(response_data)

    def get_all_lists(self, user_internal_id: int) -> TypeList[ListInDB]:
        db_lists = self.list_repository.get_user_lists(user_internal_id)
        return [ListInDB.model_validate(db_list) for db_list in db_lists]

    def get_list(self, list_id: int, user_internal_id: int) -> ListInDB:
        if not self.list_user_repository.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("You don't have access to this list")
        
        db_list = self.list_repository.get_list_by_id(list_id, user_internal_id)
        if not db_list:
            raise NotFoundException("List not found")
        db_list.user_id_list = []
        for user in db_list.list_users:
            db_list.user_id_list.append(user.user_id)
            if user.role_type == ListRoleType.CREATOR:
                db_list.creator_id = user.user_id
        
        return ListInDB.model_validate(db_list)

    def update_list(self, list_id: int, list_update: ListUpdate, user_internal_id: int) -> ListInDB:
        if not self.list_user_repository.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("You don't have access to this list")
        
        from app.services.lock_service import LockService
        lock_service = LockService(self.db)
        if not lock_service.check_lock(list_id, user_internal_id):
            raise LockException("List is locked by another user")
        
        update_data = list_update.model_dump(exclude_unset=True)
        updated_list = self.list_repository.update(list_id, update_data)
        
        if not updated_list:
            raise NotFoundException("List not found")
        
        logger.info(f"Updated list {list_id} by user {user_internal_id}")
        return ListInDB.model_validate(updated_list)

    def delete_list(self, list_id: int, user_internal_id: int) -> Dict[str, str]:
        creator = self.list_user_repository.get_creator_by_list_id(list_id)
        if not creator or creator.user_id != user_internal_id:
            raise PermissionException("Only the creator can delete the list")
        
        db_list = self.list_repository.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        success = self.list_repository.delete(list_id)
        if not success:
            raise NotFoundException("List not found")
        
        logger.info(f"Deleted list {list_id} by creator {user_internal_id}")
        return {"message": "List deleted successfully", "list_id": str(list_id)}

    def add_user_to_list(self, list_id: int, user_external_id_to_add: str, requester_internal_id: int) -> ListInDB:
        if not self.list_user_repository.user_has_role(requester_internal_id, list_id, ListRoleType.CREATOR):
            raise ForbiddenException("Only the creator can add users to this list")
        
        db_list = self.list_repository.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        user_to_add = self.user_repository.get_or_create_by_external_id(user_external_id_to_add)
        user_internal_id_to_add = user_to_add.id
        
        if self.list_user_repository.user_has_access(user_internal_id_to_add, list_id):
            raise ValueError("User is already in this list")
        
        self.list_user_repository.create(
            user_internal_id=user_internal_id_to_add,
            list_id=list_id,
            role_type=ListRoleType.USER
        )
        
        logger.info(f"Added user {user_internal_id_to_add} to list {list_id} by {requester_internal_id}")
        return self.get_list(list_id, requester_internal_id)

    def remove_user_from_list(self, list_id: int, user_internal_id_to_remove: int, requester_internal_id: int) -> ListInDB:
        if not self.list_user_repository.user_has_role(requester_internal_id, list_id, ListRoleType.CREATOR):
            raise ForbiddenException("Only the creator can remove users from this list")
        
        if requester_internal_id == user_internal_id_to_remove:
            raise ForbiddenException("Creator cannot remove themselves from the list")
        
        db_list = self.list_repository.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        success = self.list_user_repository.delete(user_internal_id_to_remove, list_id)
        if not success:
            raise NotFoundException("User not found in this list")
        
        logger.info(f"Removed user {user_internal_id_to_remove} from list {list_id} by {requester_internal_id}")
        return self.get_list(list_id, requester_internal_id)

    def check_user_access(self, user_internal_id: int, list_id: int) -> bool:
        return self.list_user_repository.get_by_user_and_list(user_internal_id, list_id) is not None

    def update_list_description(self, list_id: int, user_internal_id: int, description: str) -> Dict[str, str]:
        if not self.list_user_repository.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("No access to this list")
        
        global_role = self.global_role_service.get_role(user_internal_id)
        global_role_type = global_role.role_type if global_role else None
        
        if global_role_type != GlobalRoleType.CLIENT:
            raise ForbiddenException("Additional restriction: only users with CLIENT global role can change list description")
        
        update_data = {"description": description}
        updated_list = self.list_repository.update(list_id, update_data)
        if not updated_list:
            raise NotFoundException("List not found")
        
        logger.info(f"Updated list {list_id} description by user {user_internal_id}")
        return {"message": "List description updated successfully"}
