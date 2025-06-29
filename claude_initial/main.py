# requirements.txt
fastapi == 0.104.1
uvicorn == 0.24.0
sqlalchemy == 2.0.23
pydantic == 2.5.0
python - multipart == 0.0.6

# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.api.routes import lists, products, categories
from app.core.dependencies import get_database

app = FastAPI(
    title="House Maintenance Product Sharing API",
    description="Backend for sharing house maintenance product lists between clients and workers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lists.router, prefix="/api/v1", tags=["lists"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(categories.router, prefix="/api/v1", tags=["categories"])


@app.on_event("startup")
async def startup_event():
    create_tables()


@app.get("/")
async def root():
    return {"message": "House Maintenance Product Sharing API"}


# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./house_maintenance.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# app/core/dependencies.py
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.list_repository import ListRepository
from app.repositories.product_repository import ProductRepository
from app.services.list_service import ListService
from app.services.product_service import ProductService
from fastapi import Depends


def get_database() -> Session:
    return next(get_db())


def get_list_repository(db: Session = Depends(get_database)) -> ListRepository:
    return ListRepository(db)


def get_product_repository(db: Session = Depends(get_database)) -> ProductRepository:
    return ProductRepository(db)


def get_list_service(
        list_repo: ListRepository = Depends(get_list_repository)
) -> ListService:
    return ListService(list_repo)


def get_product_service(
        product_repo: ProductRepository = Depends(get_product_repository),
        list_repo: ListRepository = Depends(get_list_repository)
) -> ProductService:
    return ProductService(product_repo, list_repo)


# app/models/product_list.py
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class ProductList(Base):
    __tablename__ = "product_lists"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="House Maintenance List")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with products
    products = relationship("Product", back_populates="product_list", cascade="all, delete-orphan")

    def __init__(self, title: str = None, description: str = None):
        self.id = str(uuid.uuid4())
        self.title = title or "House Maintenance List"
        self.description = description
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def shareable_link(self) -> str:
        """Generate shareable link for this list"""
        return f"/lists/{self.id}"

    @property
    def product_count(self) -> int:
        """Get number of products in this list"""
        return len(self.products) if self.products else 0

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.utcnow()


# app/models/product.py
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=True)
    category = Column(String(255), nullable=False)
    subcategory = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key to product list
    list_id = Column(String, ForeignKey("product_lists.id"), nullable=False)

    # Relationship
    product_list = relationship("ProductList", back_populates="products")

    def __init__(self, name: str, category: str, quantity: int = 1,
                 description: str = None, price: float = None,
                 subcategory: str = None, list_id: str = None):
        self.id = str(uuid.uuid4())
        self._name = None
        self._category = None
        self._quantity = None

        # Use properties for validation
        self.name = name
        self.category = category
        self.quantity = quantity
        self.description = description
        self.price = price
        self.subcategory = subcategory
        self.list_id = list_id
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Product name cannot be empty")
        self._name = value.strip()

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str):
        if not value or not value.strip():
            raise ValueError("Product category cannot be empty")
        self._category = value.strip()

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        self._quantity = value

    @property
    def total_price(self) -> float:
        """Calculate total price based on quantity and unit price"""
        if self.price is None:
            return None
        return self.price * self.quantity

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.utcnow()


# app/schemas/product_list.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.schemas.product import ProductResponse


class ProductListBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="List title")
    description: Optional[str] = Field(None, description="List description")


class ProductListCreate(ProductListBase):
    pass


class ProductListUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProductListResponse(ProductListBase):
    id: str
    created_at: datetime
    updated_at: datetime
    shareable_link: str
    product_count: int
    products: List[ProductResponse] = []

    class Config:
        from_attributes = True


class ProductListSummary(BaseModel):
    id: str
    title: str
    product_count: int
    created_at: datetime
    updated_at: datetime
    shareable_link: str

    class Config:
        from_attributes = True


# app/schemas/product.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    quantity: int = Field(..., ge=0, description="Product quantity")
    price: Optional[float] = Field(None, ge=0, description="Product price per unit")
    category: str = Field(..., min_length=1, max_length=255, description="Product category")
    subcategory: Optional[str] = Field(None, max_length=255, description="Product subcategory")


class ProductCreate(ProductBase):
    @validator('name', 'category')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=255)
    subcategory: Optional[str] = Field(None, max_length=255)

    @validator('name', 'category')
    def validate_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty')
        return v.strip() if v else v


class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    total_price: Optional[float]

    class Config:
        from_attributes = True


# app/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    def __init__(self, db: Session):
        self._db = db

    @property
    def db(self) -> Session:
        return self._db

    @abstractmethod
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[ModelType]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        pass

    @abstractmethod
    def update(self, id: str, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        pass


# app/repositories/list_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.product_list import ProductList
from app.schemas.product_list import ProductListCreate, ProductListUpdate
from app.repositories.base_repository import BaseRepository


class ListRepository(BaseRepository[ProductList, ProductListCreate, ProductListUpdate]):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, obj_in: ProductListCreate) -> ProductList:
        db_obj = ProductList(
            title=obj_in.title,
            description=obj_in.description
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: str) -> Optional[ProductList]:
        return self.db.query(ProductList) \
            .options(joinedload(ProductList.products)) \
            .filter(ProductList.id == id) \
            .first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ProductList]:
        return self.db.query(ProductList) \
            .offset(skip) \
            .limit(limit) \
            .all()

    def update(self, id: str, obj_in: ProductListUpdate) -> Optional[ProductList]:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None

        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.update_timestamp()
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: str) -> bool:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True


# app/repositories/product_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, obj_in: ProductCreate, list_id: str) -> Product:
        db_obj = Product(
            name=obj_in.name,
            description=obj_in.description,
            quantity=obj_in.quantity,
            price=obj_in.price,
            category=obj_in.category,
            subcategory=obj_in.subcategory,
            list_id=list_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.db.query(Product) \
            .offset(skip) \
            .limit(limit) \
            .all()

    def get_by_list_id(self, list_id: str) -> List[Product]:
        return self.db.query(Product) \
            .filter(Product.list_id == list_id) \
            .all()

    def update(self, id: str, obj_in: ProductUpdate) -> Optional[Product]:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None

        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.update_timestamp()
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: str) -> bool:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False

        self.db.delete(db_obj)
        self.db.commit()
        return True


# app/services/list_service.py
from typing import List, Optional
from app.repositories.list_repository import ListRepository
from app.schemas.product_list import ProductListCreate, ProductListUpdate, ProductListResponse
from app.models.product_list import ProductList


class ListService:
    def __init__(self, list_repository: ListRepository):
        self._list_repository = list_repository

    def create_list(self, list_data: ProductListCreate) -> ProductListResponse:
        """Create a new product list"""
        db_list = self._list_repository.create(list_data)
        return self._to_response(db_list)

    def get_list(self, list_id: str) -> Optional[ProductListResponse]:
        """Get product list by ID"""
        db_list = self._list_repository.get_by_id(list_id)
        if not db_list:
            return None
        return self._to_response(db_list)

    def update_list(self, list_id: str, list_data: ProductListUpdate) -> Optional[ProductListResponse]:
        """Update product list"""
        db_list = self._list_repository.update(list_id, list_data)
        if not db_list:
            return None
        return self._to_response(db_list)

    def delete_list(self, list_id: str) -> bool:
        """Delete product list"""
        return self._list_repository.delete(list_id)

    def list_exists(self, list_id: str) -> bool:
        """Check if list exists"""
        return self._list_repository.get_by_id(list_id) is not None

    def _to_response(self, db_list: ProductList) -> ProductListResponse:
        """Convert database model to response schema"""
        return ProductListResponse(
            id=db_list.id,
            title=db_list.title,
            description=db_list.description,
            created_at=db_list.created_at,
            updated_at=db_list.updated_at,
            shareable_link=db_list.shareable_link,
            product_count=db_list.product_count,
            products=[self._product_to_response(p) for p in (db_list.products or [])]
        )

    def _product_to_response(self, product):
        """Helper to convert product to response format"""
        from app.schemas.product import ProductResponse
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            quantity=product.quantity,
            price=product.price,
            category=product.category,
            subcategory=product.subcategory,
            created_at=product.created_at,
            updated_at=product.updated_at,
            total_price=product.total_price
        )


# app/services/product_service.py
from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.repositories.list_repository import ListRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.models.product import Product


class ProductService:
    def __init__(self, product_repository: ProductRepository, list_repository: ListRepository):
        self._product_repository = product_repository
        self._list_repository = list_repository

    def create_product(self, list_id: str, product_data: ProductCreate) -> Optional[ProductResponse]:
        """Create a new product in a list"""
        # Verify list exists
        if not self._list_repository.get_by_id(list_id):
            return None

        db_product = self._product_repository.create(product_data, list_id)

        # Update list timestamp
        db_list = self._list_repository.get_by_id(list_id)
        if db_list:
            db_list.update_timestamp()
            self._list_repository.db.commit()

        return self._to_response(db_product)

    def get_product(self, product_id: str) -> Optional[ProductResponse]:
        """Get product by ID"""
        db_product = self._product_repository.get_by_id(product_id)
        if not db_product:
            return None
        return self._to_response(db_product)

    def get_products_by_list(self, list_id: str) -> List[ProductResponse]:
        """Get all products in a list"""
        db_products = self._product_repository.get_by_list_id(list_id)
        return [self._to_response(p) for p in db_products]

    def update_product(self, product_id: str, product_data: ProductUpdate) -> Optional[ProductResponse]:
        """Update product"""
        db_product = self._product_repository.update(product_id, product_data)
        if not db_product:
            return None

        # Update list timestamp
        db_list = self._list_repository.get_by_id(db_product.list_id)
        if db_list:
            db_list.update_timestamp()
            self._list_repository.db.commit()

        return self._to_response(db_product)

    def delete_product(self, product_id: str) -> bool:
        """Delete product"""
        db_product = self._product_repository.get_by_id(product_id)
        if not db_product:
            return False

        list_id = db_product.list_id
        success = self._product_repository.delete(product_id)

        if success:
            # Update list timestamp
            db_list = self._list_repository.get_by_id(list_id)
            if db_list:
                db_list.update_timestamp()
                self._list_repository.db.commit()

        return success

    def _to_response(self, db_product: Product) -> ProductResponse:
        """Convert database model to response schema"""
        return ProductResponse(
            id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            quantity=db_product.quantity,
            price=db_product.price,
            category=db_product.category,
            subcategory=db_product.subcategory,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at,
            total_price=db_product.total_price
        )


# app/core/categories.py
categories = {
    "Отделочные материалы": {
        "Шпатлевка": [
            "Финишная шпатлевка",
            "Стартовая шпатлевка",
            "Гипсовая шпатлевка",
            "Цементная шпатлевка",
            "Акриловая шпатлевка",
            "Полимерная шпатлевка",
            "Универсальная шпатлевка",
            "Шпатлевка по дереву",
            "Шпатлевка для влажных помещений"
        ],
        "Грунтовка": [
            "Глубокого проникновения",
            "Универсальная грунтовка",
            "Адгезионная грунтовка",
            "Акриловая грунтовка",
            "Антисептическая грунтовка",
            "Грунтовка по металлу"
        ],
        "Плиточный клей": [
            "Клей для керамической плитки",
            "Клей для керамогранита",
            "Эластичный плиточный клей",
            "Быстротвердеющий плиточный клей",
            "Клей для наружных работ",
            "Клей для теплого пола"
        ],
        "Обои": [
            "Обои флизелиновые",
            "Обои виниловые",
            "Обои бумажные",
            "Обои стеклотканевые",
            "Моющиеся обои"
        ],
        "Штукатурка": [
            "Гипсовая штукатурка",
            "Цементно-песчаная штукатурка",
            "Известковая штукатурка",
            "Декоративная штукатурка",
            "Фасадная штукатурка"
        ],
        "Краски": [
            "Водоэмульсионная краска",
            "Акриловая краска",
            "Латексная краска",
            "Силикатная краска",
            "Фасадная краска",
            "Краска по металлу",
            "Краска по дереву"
        ],
        "Герметики и силиконы": [
            "Акриловый герметик",
            "Силиконовый герметик",
            "Полиуретановый герметик",
            "Монтажный клей"
        ]
    },
    "Строительные материалы": {
        "Гипсокартон": [
            "ГКЛ стандартный",
            "ГКЛ влагостойкий",
            "ГКЛ огнестойкий",
            "Арочный гипсокартон"
        ],
        "Профиль металлический": [
            "Профиль направляющий",
            "Профиль стоечный",
            "Профиль потолочный",
            "Усиленный профиль",
            "Угловой профиль"
        ],
        "Пена монтажная": [
            "Профессиональная пена",
            "Бытовая пена",
            "Зимняя пена",
            "Летняя пена",
            "Огнестойкая пена"
        ],
        "Утеплитель": [
            "Минеральная вата",
            "Каменная вата",
            "Пенопласт",
            "Экструдированный пенополистирол (ЭППС)",
            "Пенофол",
            "Фольгированный утеплитель"
        ],
        "Цемент": [
            "Портландцемент",
            "Цемент М400",
            "Цемент М500",
            "Цемент с добавками"
        ],
        "Песок и щебень": [
            "Карьерный песок",
            "Речной песок",
            "Мелкий щебень",
            "Средний щебень",
            "Гравий"
        ],
        "Арматура и металлопрокат": [
            "Арматура 10 мм",
            "Арматура 12 мм",
            "Проволока вязальная",
            "Сетка кладочная",
            "Металлический уголок"
        ]
    },
    "Напольные покрытия": {
        "Ламинат": [
            "Ламинат 32 класса",
            "Ламинат 33 класса",
            "Ламинат влагостойкий",
            "Ламинат под дерево",
            "Ламинат под плитку"
        ],
        "Паркет": [
            "Массивная доска",
            "Паркетная доска",
            "Инженерная доска",
            "Художественный паркет"
        ],
        "Линолеум": [
            "Бытовой линолеум",
            "Коммерческий линолеум",
            "Полукоммерческий линолеум",
            "Линолеум с утеплителем"
        ],
        "Ковролин": [
            "Петлевой ковролин",
            "Разрезной ковролин",
            "Иглопробивной ковролин",
            "Ковролин с резиновой основой"
        ],
        "Плитка ПВХ (виниловая)": [
            "Клеевая плитка ПВХ",
            "Замковая плитка ПВХ",
            "Кварцвиниловая плитка"
        ],
        "Подложка под покрытие": [
            "Пробковая подложка",
            "Пенополистирольная подложка",
            "Полиэтиленовая подложка",
            "Комбинированная подложка"
        ]
    },
    "Инженерные системы": {
        "Электрика": [
            "Кабели и провода",
            "Розетки и выключатели",
            "Автоматические выключатели",
            "Короба и каналы",
            "УЗО и дифавтоматы"
        ],
        "Водоснабжение": [
            "Полипропиленовые трубы",
            "Фитинги",
            "Смесители",
            "Счетчики воды",
            "Краны шаровые"
        ],
        "Канализация": [
            "ПВХ трубы",
            "Тройники и отводы",
            "Сифоны",
            "Герметики для канализации"
        ],
        "Отопление": [
            "Алюминиевые радиаторы",
            "Биметаллические радиаторы",
            "Трубы для отопления",
            "Краны Маевского",
            "Коллекторы"
        ]
    }
}


class CategoryService:
    @staticmethod
    def get_all_categories():
        """Get all categories with subcategories and products"""
        return categories

    @staticmethod
    def get_main_categories():
        """Get only main category names"""
        return list(categories.keys())

    @staticmethod
    def get_subcategories(main_category: str):
        """Get subcategories for a main category"""
        return list(categories.get(main_category, {}).keys())

    @staticmethod
    def get_products(main_category: str, subcategory: str):
        """Get products for a specific subcategory"""
        return categories.get(main_category, {}).get(subcategory, [])

    @staticmethod
    def validate_category(category: str, subcategory: str = None):
        """Validate if category and subcategory exist"""
        if category not in categories:
            return False

        if subcategory and subcategory not in categories[category]:
            return False

        return True


# app/api/routes/lists.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.list_service import ListService
from app.schemas.product_list import ProductListCreate, ProductListUpdate, ProductListResponse
from app.core.dependencies import get_list_service

router = APIRouter()


@router.post("/lists/", response_model=ProductListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
        list_data: ProductListCreate,
        list_service: ListService = Depends(get_list_service)
):
    """Create a new product list"""
    try:
        return list_service.create_list(list_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create list: {str(e)}"
        )


@router.get("/lists/{list_id}", response_model=ProductListResponse)
async def get_list(
        list_id: str,
        list_service: ListService = Depends(get_list_service)
):
    """Get a product list by ID"""
    list_data = list_service.get_list(list_id)
    if not list_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    return list_data


@router.put("/lists/{list_id}", response_model=ProductListResponse)
async def update_list(
        list_id: str,
        list_data: ProductListUpdate,
        list_service: ListService = Depends(get_list_service)
):
    """Update a product list"""
    updated_list = list_service.update_list(list_id, list_data)
    if not updated_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    return updated_list


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
        list_id: str,
        list_service: ListService = Depends(get_list_service)
):
    """Delete a product list"""
    success = list_service.delete_list(list_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )


# app/api/routes/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.product_service import ProductService
from app.services.list_service import ListService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.dependencies import get_product_service, get_list_service

router = APIRouter()


@router.post("/lists/{list_id}/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
        list_id: str,
        product_data: ProductCreate,
        product_service: ProductService = Depends(get_product_service),
        list_service: ListService = Depends(get_list_service)
):
    """Add a product to a list"""
    # Verify list exists
    if not list_service.list_exists(list_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )

    try:
        product = product_service.create_product(list_id, product_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create product"
            )
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/lists/{list_id}/products/", response_model=List[ProductResponse])
async def get_products_by_list(
        list_id: str,
        product_service: ProductService = Depends(get_product_service),
        list_service: ListService = Depends(get_list_service)
):
    """Get all products in a list"""
    if not list_service.list_exists(list_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )

    return product_service.get_products_by_list(list_id)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
        product_id: str,
        product_service: ProductService = Depends(get_product_service)
):
    """Get a product by ID"""
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
        product_id: str,
        product_data: ProductUpdate,
        product_service: ProductService = Depends(get_product_service)
):
    """Update a product"""
    try:
        updated_product = product_service.update_product(product_id, product_data)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return updated_product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
        product_id: str,
        product_service: ProductService = Depends(get_product_service)
):
    """Delete a product"""
    success = product_service.delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )


# app/api/routes/categories.py
from fastapi import APIRouter
from typing import Dict, List
from app.core.categories import CategoryService

router = APIRouter()


@router.get("/categories/", response_model=Dict)
async def get_all_categories():
    """Get all categories with subcategories and products"""
    return CategoryService.get_all_categories()


@router.get("/categories/main/", response_model=List[str])
async def get_main_categories():
    """Get main category names only"""
    return CategoryService.get_main_categories()


@router.get("/categories/{main_category}/subcategories/", response_model=List[str])
async def get_subcategories(main_category: str):
    """Get subcategories for a main category"""
    subcategories = CategoryService.get_subcategories(main_category)
    if not subcategories:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Main category not found"
        )
    return subcategories


@router.get("/categories/{main_category}/{subcategory}/products/", response_model=List[str])
async def get_category_products(main_category: str, subcategory: str):
    """Get products for a specific subcategory"""
    products = CategoryService.get_products(main_category, subcategory)
    if not products:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category or subcategory not found"
        )
    return products

# app/api/__init__.py
# Empty file to make it a package

# app/api/routes/__init__.py
# Empty file to make it a package

# How to run the application:
# 1. Install dependencies: pip install -r requirements.txt
# 2. Run the server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 3. Access API documentation: http://localhost:8000/docs

# Example API Usage:

# 1. Create a new list:
# POST /api/v1/lists/
# {
#     "title": "Ремонт кухни",
#     "description": "Список материалов для ремонта кухни"
# }

# 2. Add products to the list:
# POST /api/v1/lists/{list_id}/products/
# {
#     "name": "Финишная шпатлевка Knauf",
#     "description": "Для финишного выравнивания стен",
#     "quantity": 2,
#     "price": 450.00,
#     "category": "Отделочные материалы",
#     "subcategory": "Шпатлевка"
# }

# 3. Get list with all products:
# GET /api/v1/lists/{list_id}

# 4. Get categories:
# GET /api/v1/categories/

# 5. Share the list using the shareable_link from the response
# The link format will be: /lists/{list_id}

# Key Features Implemented:
# - SOLID Principles: Single Responsibility, Open/Closed, Dependency Inversion
# - Proper Encapsulation with private methods and property decorators
# - Modular architecture with separate layers (models, repositories, services, API)
# - Repository pattern for data access abstraction
# - Service layer for business logic
# - Comprehensive error handling and validation
# - UUID-based shareable links
# - Russian house maintenance categories
# - Easy extensibility for future features

# Database will be created automatically as house_maintenance.db in the project root