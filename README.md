
# List Editor

A list management application that provides secure, participant-based collaboration on shared lists.

## Overview

List Editor is a collaborative list management system designed for teams and individuals who need to share and manage lists efficiently. Built with modern Python technologies, it provides a robust API for creating, sharing, and managing lists with collaboration features.

### Key Highlights

- **Participant-based Access Control**: Fine-grained permissions for list creators and participants
- **Collaboration**: Concurrent editing with locking mechanisms
- **User ID-based Authentication**: Secure login with internal and external user IDs.
- **RESTful API**: Clean, well-documented API endpoints
- **Scalable Architecture**: Modular design following clean architecture principles

## Features

### Core Functionality

#### List Management
-  **Create Lists**: Users can create new lists with optional initial items
-  **List Ownership**: Each list has a designated creator with special privileges
-  **Participant Management**: Creators can add/remove participants to their lists
-  **List Updates**: All participants can modify list metadata
-  **List Deletion**: Only creators can permanently delete lists

#### Item Management
-  **Add Items**: All participants can add items to shared lists
-  **Update Items**: Modify item details (name, category, quantity, price)
-  **Delete Items**: Remove items from lists
-  **Item Categorization**: Organize items by categories
-  **Price Tracking**: Track item prices and quantities

#### Collaboration Features
-  **Participant Access**: Share lists with specific users
-  **Concurrent Editing**: Multiple users can edit simultaneously
-  **Lock Management**: FIFO locking system prevents conflicts
-  **Real-time Notifications**: In-app notifications for list changes
-  **Activity Tracking**: Audit trail for all list modifications

#### Security & Access Control
-  **User ID Authentication**: Secure login using an external ID from the `X-User-ID` header, with all subsequent operations using an internal integer ID.
-  **Role-based Permissions**: Creator vs. participant privilege levels
-  **Access Validation**: Strict access control on all operations
-  **Data Isolation**: Users only see lists they have access to
-  **Participant Management**: Add and remove users from lists (creator only)

#### Technical Features
-  **RESTful API**: Clean, intuitive API design
-  **Data Validation**: Comprehensive input validation with Pydantic
-  **Error Handling**: Detailed error responses and logging
-  **Database Persistence**: PostgreSQL with SQLAlchemy ORM
-  **Automatic Timestamps**: Creation and modification tracking
-  **CORS Support**: Cross-origin resource sharing enabled
-  **Containerization**: Docker support for easy deployment

## Architecture

The application follows a layered architecture pattern with clear separation of concerns:
```
┌─────────────────┐
│   API Layer     │  ← FastAPI endpoints, request/response handling
├─────────────────┤
│  Service Layer  │  ← Business logic, access control, notifications
├─────────────────┤
│Repository Layer │  ← Data access, database operations
├─────────────────┤
│   Model Layer   │  ← SQLAlchemy models, database schema
└─────────────────┘
```

#### 1. API Layer (`app/api/`)
- **Endpoints**: FastAPI route handlers for HTTP requests
- **Dependencies**: Dependency injection for services and authentication
- **Request/Response**: HTTP request processing and response formatting

#### 2. Service Layer (`app/services/`)
- **Business Logic**: Core application logic and workflows
- **Data Orchestration**: Coordination between multiple repositories
- **Validation**: Business rule validation and enforcement
- **Notifications**: User notification and messaging services

#### 3. Repository Layer (`app/repositories/`)
- **Data Access**: Database operations and query management
- **CRUD Operations**: Create, Read, Update, Delete operations for entities
- **Query Optimization**: Efficient database queries and relationships
- **Transaction Management**: Database transaction handling

#### 4. Model Layer (`app/models/`)
- **Database Schema**: SQLAlchemy models defining table structures
- **Relationships**: Entity relationships and foreign key constraints
- **Data Integrity**: Database-level constraints and validations

#### 5. Schema Layer (`app/schemas/`)
- **Data Validation**: Pydantic models for request/response validation
- **Type Safety**: Strong typing for API contracts
- **Serialization**: Data transformation between layers

#### 6. Core Layer (`app/core/`)
- **Configuration**: Application settings and environment management
- **Database**: Database connection and session management
- **Exceptions**: Custom exception classes and error handling

#### 7. Utilities (`app/utils/`)
- **Logging**: Application logging and monitoring
- **UUID Generation**: Unique identifier creation
- **Helper Functions**: Common utility functions

### Design Principles

- **KISS (Keep It Simple, Stupid)**: Simple, maintainable solutions
- **YAGNI (You Aren't Gonna Need It)**: Implement only what's needed
- **Open/Closed Principle**: Extensible design with minimal modifications
- **Single Responsibility**: Each component has a single, well-defined purpose
- **Dependency Injection**: Loose coupling through dependency injection

## Getting Started

### Prerequisites

- **Python 3.10+** (Required)
- **pip** (Python package manager)
- **Docker** (Optional, for containerized deployment)
- **Git** (For cloning the repository)
- **Postgres** (SQL data storage)

### Installation and Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/amirullo/list_editor.git
   cd list_editor
   ```

2.**Run and Setup SQL-server (Postgres)**
   ```bash
   brew install postgresql
   brew services start postgresql
   /opt/homebrew/opt/postgresql@14/bin/createuser -s _postgres
   brew services restart postgresql@14
      
   psql -U _postgres
   CREATE DATABASE mydb;
   CREATE USER dev WITH PASSWORD 'pymbep-koxzev-hokdU6';
   GRANT ALL PRIVILEGES ON DATABASE mydb TO dev;
   
   psql -U dev -d mydb -f ddl_postgres.sql
   ```
   
3.**Run the application:**
   ```bash
   docker build -t list_editor:test .
   docker run -p 8000:8000 list_editor:test
   ```


4. **Access Application**

- API: http://localhost:8000

- Documentation: http://localhost:8000/docs

- Health Check: http://localhost:8000/health

## Project Structure
```
list_editor/
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── api/                    # API layer
│   │   ├── __init__.py
│   │   ├── dependencies.py     # Dependency injection
│   │   └── endpoints/          # API route definitions
│   │       ├── __init__.py
│   │       ├── list_endpoints.py
│   │       ├── user_endpoints.py
│   │       ├── role_endpoints.py
│   │       └── sync_endpoints.py
│   │
│   ├── core/                   # Core configuration and setup
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   ├── db.py               # Database connection and session
│   │   └── exceptions.py       # Custom exception classes
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py             # Base model with common fields
│   │   ├── list_model.py       # List entity model
│   │   ├── item_model.py       # Item entity model
│   │   ├── user_model.py       # User entity model
│   │   ├── lock_model.py       # Lock entity model
│   │   ├── global_role_model.py # Global Role entity model
│   │   └── list_role_model.py  # List Role entity model
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py  # Generic repository pattern
│   │   ├── list_repository.py  # List-specific data operations
│   │   ├── item_repository.py  # Item-specific data operations
│   │   ├── user_repository.py  # User-specific data operations
│   │   └── role_repository.py  # Role-specific data operations
│   │
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── list_schema.py      # List request/response schemas
│   │   ├── item_schema.py      # Item request/response schemas
│   │   ├── user_schema.py      # User request/response schemas
│   │   ├── role_schema.py      # Role request/response schemas
│   │   └── response_schema.py  # Generic response schemas
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── list_service.py     # List business logic
│   │   ├── item_service.py     # Item business logic
│   │   ├── role_service.py     # Role business logic
│   │   ├── lock_service.py     # Concurrency control
│   │   └── notification_service.py
│   │
│   └── utils/                  # Utility functions and helpers
│       ├── __init__.py
│       ├── logger.py           # Logging configuration
│       └── validators.py       # Custom validators
│
├──
```

## API Endpoints

### User Authentication
- `POST /api/users/login` - Login with an external user ID to get an internal user ID.

### List Management
- `POST /api/lists/` - Create a new list
- `GET /api/lists/` - Get all lists for authenticated user
- `GET /api/lists/{list_id}` - Get specific list details
- `PUT /api/lists/{list_id}` - Update list information
- `DELETE /api/lists/{list_id}` - Delete list (creator only)

### User Management
- `POST /api/lists/{list_id}/users` - Add user to list by their external ID (creator only).
- `DELETE /api/lists/{list_id}/users/{user_to_remove_external_id}` - Remove user from list by their external ID (creator only).

### Item Management
- `POST /api/lists/{list_id}/items` - Create new item in list
- `GET /api/lists/{list_id}/items` - Get all items in list
- `PUT /api/lists/{list_id}/items/{item_id}` - Update item
- `DELETE /api/lists/{list_id}/items/{item_id}` - Delete item

### Locking System
- `POST /api/lists/{list_id}/lock` - Acquire lock on list
- `DELETE /api/lists/{list_id}/lock` - Release lock on list

### Synchronization
- `POST /api/lists/{list_id}/sync` - Manual synchronization endpoint
- `GET /api/sync/notifications` - Get notifications for changes

### Role Management
- `POST /api/roles/global` - Create a new global role for a user.
- `GET /api/roles/global/{user_internal_id}` - Get the global role for a user.
- `GET /api/roles/list/{list_id}/{user_internal_id}` - Get the list role for a user.

## Data Models

### User
- id: Integer primary key (internal ID)
- external_id: String (unique, for login)

### List
- id: Integer primary key
- name: String (required)
- description: Text (optional)
- created_at: Timestamp
- updated_at: Timestamp

### Item
- id: Integer primary key
- name: String (required)
- description: Text (optional)
- quantity: Integer (default: 1)
- price: Float (optional)
- category: String (optional)
- list_id: Foreign key to List

### ListUser (Association)
- list_id: Foreign key to List
- user_id: Foreign key to User (internal ID)
- role_type: Enum (CREATOR, USER)

### Lock
- id: Integer primary key
- list_id: Foreign key to List
- holder_id: Foreign key to User (internal ID)

### GlobalRole
- id: Integer primary key
- user_id: Foreign key to User (internal ID)
- role_type: Enum (CLIENT, WORKER)

### ListRole
- id: Integer primary key
- role_type: Enum (CREATOR, USER)
- description: String (optional)


## Error Handling
   The API returns structured error responses:
   ```
   {
     "status": "error",
     "message": "Descriptive error message",
     "data": null
   }
   ```
### Common HTTP status codes:
- 200: Success
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing/invalid user ID)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 409: Conflict (locking conflicts)
- 500: Internal Server Error

## Roles 

### Global roles
- CLIENT - only he can change (WORKER can't change) the price of an item.
- WORKER - only he can change (CLIENT can't change) the quantity of an item.


### List roles (Global role restrictions override List role privileges)
- CREATOR - who created the list. only he can delete the list. he has full access to the list and corresponding items to the list, until he has restrictions on Global role level.
- USER - additional users that can read everything in the list and corresponding items to the list, and can modify the list and its items, until he has restrictions on Global role level.

### Examples: 
- CREATOR + CLIENT: Can do everything including change price, but NOT quantity
- CREATOR + WORKER: Can do everything including change quantity, but NOT price  
- USER + CLIENT: Can modify the list and its items, including price, but NOT quantity
- USER + WORKER: Can modify the list and its items, including quantity, but NOT price
