
# List Editor

A list management application that provides secure, participant-based collaboration on shared lists.

## Overview

List Editor is a collaborative list management system designed for teams and individuals who need to share and manage lists efficiently. Built with modern Python technologies, it provides a robust API for creating, sharing, and managing lists with collaboration features.

### Key Highlights

- **Participant-based Access Control**: Fine-grained permissions for list creators and participants
- **Collaboration**: Concurrent editing with locking mechanisms
- **UUID-based Authentication**: Secure, stateless authentication system
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
-  **UUID Authentication**: Secure, token-free authentication
-  **Role-based Permissions**: Creator vs. participant privilege levels
-  **Access Validation**: Strict access control on all operations
-  **Data Isolation**: Users only see lists they have access to
-  **Participant Management**: Add and remove users from lists (creator only)

#### Technical Features
-  **RESTful API**: Clean, intuitive API design
-  **Data Validation**: Comprehensive input validation with Pydantic
-  **Error Handling**: Detailed error responses and logging
-  **Database Persistence**: SQLite with SQLAlchemy ORM
-  **Automatic Timestamps**: Creation and modification tracking
-  **CORS Support**: Cross-origin resource sharing enabled
-  **Containerization**: Docker support for easy deployment

## Architecture

### System Design

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

### Installation and Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/amirullo/list_editor.git
   cd list_editor
   ```
2. **Run the application:**
   ```bash
   docker build -t list_editor:test .
   docker run -p 8000:8000 list_editor:test
   ```
3. **Run script examples (interact with) :**
   ```bash
   python ./scripts/create_list.py
   python ./scripts/worker.py
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
│   │       └── role_endpoints.py
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
│   │   ├── role_model.py       # Role entity model
│   │   └── notification_model.py
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py  # Generic repository pattern
│   │   ├── list_repository.py  # List-specific data operations
│   │   ├── item_repository.py  # Item-specific data operations
│   │   └── role_repository.py  # Role-specific data operations
│   │
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── list_schema.py      # List request/response schemas
│   │   ├── item_schema.py      # Item request/response schemas
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

### List Management
- `POST /api/lists/` - Create a new list
- `GET /api/lists/` - Get all lists for authenticated user
- `GET /api/lists/{list_id}` - Get specific list details
- `PUT /api/lists/{list_id}` - Update list information
- `DELETE /api/lists/{list_id}` - Delete list (creator only)

### User Management
- `POST /api/lists/{list_id}/users` - Add user to list (creator only)
- `DELETE /api/lists/{list_id}/users/{user_id}` - Remove user from list (creator only)

### Item Management
- `POST /api/lists/{list_id}/items` - Create new item in list
- `GET /api/lists/{list_id}/items` - Get all items in list
- `PUT /api/lists/{list_id}/items/{item_id}` - Update item
- `DELETE /api/lists/{list_id}/items/{item_id}` - Delete item

### Locking System
- `POST /api/lists/{list_id}/lock` - Acquire lock on list
- `DELETE /api/lists/{list_id}/lock` - Release lock on list

### Synchronization
- `GET /api/sync/{list_id}` - Manual synchronization endpoint

### Role Management
- `GET /api/roles/` - Get available roles
- `POST /api/roles/assign` - Assign role to user

## Data Models

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
- completed: Boolean (default: false)
- list_id: Foreign key to List

### ListUser (Association)
   - list_id: Foreign key to List
   - user_id: UUID string
   - role: Enum (creator, participant)
   - joined_at: Timestamp

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
- CLIENT - only he can change (WORKER can't change) description of the list and can change price of the item.
- WORKER - only he can change (CLIENT can't change) quantity of the item.


### List roles (Global role restrictions override List role privileges)
- CREATOR - who created the list. only he can delete the list. he has full access to the list and corresponding items to the list, until he has restrictions on Global role level.
- USER - additional users that can read everything in the list and corresponding items to the list, and modify some parts of the list: add or modify items, until he has restrictions on Global role level.

### Examples: 
- CREATOR + CLIENT: Can do everything including change price, but NOT quantity
- CREATOR + WORKER: Can do everything including change quantity, but NOT price  
- USER + CLIENT: Can modify items including price, but NOT quantity
- USER + WORKER: Can modify items including quantity, but NOT price