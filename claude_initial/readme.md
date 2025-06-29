# House Maintenance Product Sharing API

A professional FastAPI backend for sharing house maintenance product lists between clients and workers. Built with SOLID principles, clean architecture, and enterprise-grade design patterns.

## 🏗️ Architecture

### Design Principles
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Clean Architecture**: Separation of concerns with distinct layers
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: Loosely coupled components

### Project Structure
```
app/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── database.py         # Database configuration and session management
│   ├── dependencies.py     # Dependency injection container
│   └── categories.py       # Category service and data
├── models/
│   ├── product_list.py     # ProductList SQLAlchemy model
│   └── product.py          # Product SQLAlchemy model
├── schemas/
│   ├── product_list.py     # ProductList Pydantic schemas
│   └── product.py          # Product Pydantic schemas
├── repositories/
│   ├── base_repository.py  # Abstract base repository
│   ├── list_repository.py  # ProductList data access
│   └── product_repository.py # Product data access
├── services/
│   ├── list_service.py     # ProductList business logic
│   └── product_service.py  # Product business logic
└── api/
    └── routes/
        ├── lists.py        # ProductList API endpoints
        ├── products.py     # Product API endpoints
        └── categories.py   # Category API endpoints
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd house-maintenance-api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the API**
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/

## 📊 Database

### Current Setup
- **Database**: SQLite (development)
- **ORM**: SQLAlchemy
- **Migration**: Auto-creation on startup
- **File Location**: `./house_maintenance.db`

### Production Considerations
The architecture supports easy migration to production databases:
- **Recommended**: ClickHouse (as mentioned in requirements)
- **Alternatives**: PostgreSQL, MySQL, etc.
- **Configuration**: Update `DATABASE_URL` environment variable

### Models

#### ProductList
```python
- id: str (UUID, Primary Key)
- title: str (max 255 chars)
- description: str (optional)
- created_at: datetime
- updated_at: datetime
- products: List[Product] (relationship)
```

#### Product
```python
- id: str (UUID, Primary Key)
- name: str (required, max 255 chars)
- description: str (optional)
- quantity: int (required, >= 0)
- price: float (optional, >= 0)
- category: str (required, max 255 chars)
- subcategory: str (optional, max 255 chars)
- list_id: str (Foreign Key)
- created_at: datetime
- updated_at: datetime
```

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Product Lists

#### Create List
```http
POST /lists/
Content-Type: application/json

{
    "title": "Ремонт кухни",
    "description": "Список материалов для ремонта кухни"
}
```

#### Get List
```http
GET /lists/{list_id}
```

#### Update List
```http
PUT /lists/{list_id}
Content-Type: application/json

{
    "title": "Updated title",
    "description": "Updated description"
}
```

#### Delete List
```http
DELETE /lists/{list_id}
```

### Products

#### Add Product to List
```http
POST /lists/{list_id}/products/
Content-Type: application/json

{
    "name": "Финишная шпатлевка Knauf",
    "description": "Для финишного выравнивания стен",
    "quantity": 2,
    "price": 450.00,
    "category": "Отделочные материалы",
    "subcategory": "Шпатлевка"
}
```

#### Get Products in List
```http
GET /lists/{list_id}/products/
```

#### Get Single Product
```http
GET /products/{product_id}
```

#### Update Product
```http
PUT /products/{product_id}
Content-Type: application/json

{
    "name": "Updated product name",
    "quantity": 5,
    "price": 500.00
}
```

#### Delete Product
```http
DELETE /products/{product_id}
```

### Categories

#### Get All Categories
```http
GET /categories/
```

#### Get Main Categories
```http
GET /categories/main/
```

#### Get Subcategories
```http
GET /categories/{main_category}/subcategories/
```

#### Get Category Products
```http
GET /categories/{main_category}/{subcategory}/products/
```

## 🏷️ Categories

The API includes comprehensive Russian house maintenance categories:

- **Отделочные материалы** (Finishing Materials)
  - Шпатлевка, Грунтовка, Плиточный клей, Обои, Штукатурка, Краски, Герметики и силиконы

- **Строительные материалы** (Construction Materials)
  - Гипсокартон, Профиль металлический, Пена монтажная, Утеплитель, Цемент, Песок и щебень, Арматура и металлопрокат

- **Напольные покрытия** (Floor Coverings)
  - Ламинат, Паркет, Линолеум, Ковролин, Плитка ПВХ, Подложка под покрытие

- **Инженерные системы** (Engineering Systems)
  - Электрика, Водоснабжение, Канализация, Отопление

## 🔗 Sharing Mechanism

### How It Works
1. Create a product list via API
2. Get the `shareable_link` from the response
3. Share the link with workers or clients
4. Anyone with the link can view and edit the list

### Link Format
```
/lists/{uuid}
```

### Security Model
- **Current**: UUID-based access (no authentication required)
- **Future**: Can be extended with authentication, permissions, expiration dates

## 🛠️ Development

### Code Quality
- **Linting**: Follow PEP 8 standards
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Docstrings for all public methods
- **Error Handling**: Comprehensive exception handling

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

### Adding New Features

#### Adding a New Model
1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Create API routes in `app/api/routes/`
6. Update dependencies in `app/core/dependencies.py`

#### Example: Adding User Authentication
```python
# 1. Add User model
# 2. Add authentication service
# 3. Update dependencies with auth
# 4. Add protected routes
# 5. Update existing endpoints
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/house_maintenance

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist
- [ ] Replace SQLite with production database
- [ ] Add authentication system
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Set up HTTPS
- [ ] Configure CORS properly
- [ ] Add input sanitization
- [ ] Implement backup strategy
- [ ] Add health checks
- [ ] Set up CI/CD pipeline

## 🔒 Security Considerations

### Current Security
- Input validation via Pydantic schemas
- SQL injection protection via SQLAlchemy ORM
- CORS middleware configured
- UUID-based access tokens

### Recommended Enhancements
- Add authentication (JWT tokens)
- Implement rate limiting
- Add request logging
- Input sanitization
- HTTPS enforcement
- Security headers
- API versioning

## 📈 Performance Optimization

### Current Optimizations
- SQLAlchemy ORM with connection pooling
- Async/await pattern for I/O operations
- Efficient database queries with joins
- Proper indexing on UUID fields

### Scaling Considerations
- Database connection pooling
- Caching layer (Redis)
- Database read replicas
- API rate limiting
- Load balancing
- Monitoring and alerting

## 🧪 Testing Strategy

### Test Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_repositories.py
│   └── test_services.py
├── integration/
│   └── test_api.py
└── fixtures/
    └── test_data.py
```

### Test Categories
- **Unit Tests**: Models, repositories, services
- **Integration Tests**: API endpoints, database operations
- **End-to-End Tests**: Complete workflows

## 🔄 Future Enhancements

### Planned Features
- [ ] User authentication and authorization
- [ ] Multiple lists per user
- [ ] File upload capabilities
- [ ] Real-time updates (WebSocket)
- [ ] Email notifications
- [ ] Advanced search and filtering
- [ ] Bulk operations
- [ ] Data export (PDF, Excel)
- [ ] Mobile API optimizations
- [ ] Analytics and reporting

### Architecture Improvements
- [ ] Event-driven architecture
- [ ] Microservices separation
- [ ] CQRS pattern implementation
- [ ] Message queue integration
- [ ] API Gateway
- [ ] Service mesh

## 📝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement changes following SOLID principles
4. Add comprehensive tests
5. Update documentation
6. Submit pull request

### Code Standards
- Follow PEP 8 style guide
- Use type hints consistently
- Write descriptive docstrings
- Maintain test coverage > 80%
- Keep functions focused and small

## 📞 Support

### Documentation
- API Documentation: `/docs` endpoint
- Code Documentation: Inline docstrings
- Architecture Documentation: This README

### Common Issues
- **Database not found**: Ensure SQLite permissions
- **Import errors**: Check Python path and dependencies
- **CORS issues**: Configure allowed origins properly

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **ML Engineer** - Initial work and architecture design

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- SQLAlchemy team for the robust ORM
- Pydantic team for data validation
- Russian construction industry for category specifications ***- wat??? )))***