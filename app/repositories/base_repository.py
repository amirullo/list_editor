from typing import Generic, TypeVar, Type, List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from app.models.base import BaseModel
from app.utils.logger import logger # Import logger

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: Any) -> Optional[ModelType]:
        logger.info(f"BaseRepository: Getting {self.model.__name__} with id={id}")
        result = self.db.query(self.model).filter(self.model.id == id).first()
        logger.info(f"BaseRepository: Get result for {self.model.__name__} id={id}: {result is not None}")
        return result
    
    def get_all(self) -> List[ModelType]:
        logger.info(f"BaseRepository: Getting all {self.model.__name__}s")
        return self.db.query(self.model).all()
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        logger.info(f"BaseRepository: Creating new {self.model.__name__} with data: {obj_in}")
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"BaseRepository: Created {self.model.__name__} with id={db_obj.id}")
        return db_obj
    
    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        logger.info(f"BaseRepository: Updating {self.model.__name__} with id={id} with data: {obj_in}")
        db_obj = self.get(id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"BaseRepository: Updated {self.model.__name__} with id={id}")
        return db_obj
    
    def delete(self, id: Any) -> bool:
        logger.info(f"BaseRepository: Deleting {self.model.__name__} with id={id}")
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            logger.info(f"BaseRepository: Deleted {self.model.__name__} with id={id}")
            return True
        return False