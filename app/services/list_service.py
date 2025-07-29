from typing import List as TypeList, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.lock_repository import LockRepository
from app.models.list_model import List
from app.models.item_model import Item
from app.schemas.list_schema import ListCreate, ListUpdate, ListInDB
from app.schemas.item_schema import ItemCreate
from app.core.exceptions import NotFoundException, LockException, ForbiddenException
from app.services.notification_service import NotificationService

class ListService:
    def __init__(self, list_repository: ListRepository):
        self.list_repository = list_repository

    def create_list(self, list_create: ListCreate, creator_id: str, items: TypeList[ItemCreate] = None) -> ListInDB:
        """Create a new list with creator_id"""
        list_data = list_create.model_dump()
        items_data = [item.model_dump() for item in items] if items else None
        
        db_list = self.list_repository.create_with_items(list_data, creator_id, items_data)
        
        # Notify all participants about list creation
        self._notify_list_participants(db_list, f"List '{db_list.name}' was created", creator_id)
        
        return ListInDB.model_validate(db_list)

    def get_all_lists(self, user_id: str) -> TypeList[ListInDB]:
        """Get all lists accessible to user"""
        db_lists = self.list_repository.get_user_lists(user_id)
        return [ListInDB.model_validate(db_list) for db_list in db_lists]

    def get_list(self, list_id: int, user_id: str) -> ListInDB:
        """Get list if user has access"""
        db_list = self.list_repository.get_list_by_id_and_user(list_id, user_id)
        if not db_list:
            raise NotFoundException(f"List with id {list_id} not found or access denied")
        return ListInDB.model_validate(db_list)

    def update_list(self, list_id: int, list_update: ListUpdate, user_id: str) -> ListInDB:
        """Update list - only accessible users can update"""
        # Check if user has access to the list
        db_list = self.list_repository.get_list_by_id_and_user(list_id, user_id)
        if not db_list:
            raise NotFoundException(f"List with id {list_id} not found or access denied")
        
        update_data = {k: v for k, v in list_update.model_dump().items() if v is not None}
        updated_list = self.list_repository.update(list_id, update_data)
        
        # Notify all participants about list update
        self._notify_list_participants(updated_list, f"List '{updated_list.name}' was updated", user_id)
        
        return ListInDB.model_validate(updated_list)

    def delete_list(self, list_id: int, user_id: str) -> Dict[str, str]:
        """Delete list - only creator can delete"""
        # Check if user is the creator
        db_list = self.list_repository.get_list_by_id_and_creator(list_id, user_id)
        if not db_list:
            raise ForbiddenException("Only the creator can delete this list")
        
        list_name = db_list.name
        
        # Notify all participants before deletion
        self._notify_list_participants(db_list, f"List '{list_name}' was deleted", user_id)
        
        self.list_repository.delete(list_id)
        return {"message": f"List '{list_name}' deleted successfully"}

    def add_user_to_list(self, list_id: int, user_id_to_add: str, requester_id: str) -> ListInDB:
        """Add user to list - only creator can add users"""
        # Check if requester is the creator
        db_list = self.list_repository.get_list_by_id_and_creator(list_id, requester_id)
        if not db_list:
            raise ForbiddenException("Only the creator can add users to this list")
        
        # Don't add creator to user_id_list
        if user_id_to_add == db_list.creator_id:
            raise ValueError("Creator is already part of the list")
        
        updated_list = self.list_repository.add_user_to_list(list_id, user_id_to_add)
        
        # Notify all participants about new user
        self._notify_list_participants(updated_list, f"User {user_id_to_add} was added to list '{updated_list.name}'", requester_id)
        
        return ListInDB.model_validate(updated_list)

    def remove_user_from_list(self, list_id: int, user_id_to_remove: str, requester_id: str) -> ListInDB:
        """Remove user from list - only creator can remove users"""
        # Check if requester is the creator
        db_list = self.list_repository.get_list_by_id_and_creator(list_id, requester_id)
        if not db_list:
            raise ForbiddenException("Only the creator can remove users from this list")
        
        # Can't remove creator
        if user_id_to_remove == db_list.creator_id:
            raise ValueError("Cannot remove creator from the list")
        
        updated_list = self.list_repository.remove_user_from_list(list_id, user_id_to_remove)
        
        # Notify all participants about user removal
        self._notify_list_participants(updated_list, f"User {user_id_to_remove} was removed from list '{updated_list.name}'", requester_id)
        
        return ListInDB.model_validate(updated_list)

    def _notify_list_participants(self, db_list, message: str, actor_id: str):
        """Notify all list participants about changes"""
        # Get all participants (creator + users in user_id_list)
        participants = [db_list.creator_id]
        if db_list.user_id_list:
            participants.extend(db_list.user_id_list)
        
        # Remove duplicates and the actor
        participants = list(set(participants))
        if actor_id in participants:
            participants.remove(actor_id)
        
        # Send notifications
        for participant_id in participants:
            self.notification_service.create_notification(
                user_id=participant_id,
                message=message,
                list_id=db_list.id
            )
