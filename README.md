
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
-  **List Details**: Lists can include total price, total delivery period, and a flat address.
-  **Store Locations**: Lists can include a map with store addresses.

#### Item Management
-  **Add Items**: All participants can add items to shared lists
-  **Update Items**: Modify item details (name, category, quantity, price)
-  **Delete Items**: Remove items from lists
-  **Item Categorization**: Organize items by categories
-  **Price Tracking**: Track item prices and quantities
-  **Link Parsing**: Parse item links to extract photo, price, delivery price, and delivery period.
-  **Store Information**: Items can be associated with a store, including its address and distance.
-  **Item Status**: Items have flags for "approved" (worker), "bought" (client/worker), and "delivered" (worker).

#### Project Management
- **Project Management**: Define a project with a name, planned and actual periods, total material and worker prices, and a place description.
- **Step Management**: Break down a project into steps, each with a name, planned and actual periods, material and worker prices, required items, and photos/videos of the results. Steps can have a parent step.
- **Gantt Chart**: Visualize the project timeline with a Gantt diagram.

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

#### Technical & Utility Features
-  **RESTful API**: Clean, intuitive API design
-  **Data Validation**: Comprehensive input validation with Pydantic
-  **Error Handling**: Detailed error responses and logging
-  **Database Persistence**: PostgreSQL with SQLAlchemy ORM
-  **Automatic Timestamps**: Creation and modification tracking
-  **CORS Support**: Cross-origin resource sharing enabled
-  **Containerization**: Docker support for easy deployment
-  **Logging**: Centralized application logging and monitoring
-  **Helper Functions**: Common utility functions and custom validators

## Architecture

The application follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────┐ 
│    API Layer    │  ← Endpoints & Request/Response (FastAPI)
├─────────────────┤
│   Schema Layer  │  ← Data Validation & Serialization (Pydantic)
├─────────────────┤
│  Service Layer  │  ← Business Logic & Orchestration
├─────────────────┤
│Repository Layer │  ← Data Access & Database Operations (SQLAlchemy)
├─────────────────┤
│   Model Layer   │  ← Database Schema & ORM Models
├─────────────────┤
│   Core & Utils  │  ← Config, DB Session, Exceptions, Helpers
└─────────────────┘
```

#### 1. API Layer (`app/api/`)
- **Endpoints**: FastAPI route handlers for HTTP requests
- **Dependencies**: Dependency injection for services and authentication
- **Request/Response**: HTTP request processing and response formatting

#### 2. Schema Layer (`app/schemas/`)
- **Data Validation**: Pydantic models for request/response validation
- **Type Safety**: Strong typing for API contracts
- **Serialization**: Data transformation between layers

#### 3. Service Layer (`app/services/`)
- **Business Logic**: Core application logic and workflows
- **Data Orchestration**: Coordination between multiple repositories
- **Validation**: Business rule validation and enforcement
- **Notifications**: User notification and messaging services

#### 4. Repository Layer (`app/repositories/`)
- **Data Access**: Database operations and query management
- **CRUD Operations**: Create, Read, Update, Delete operations for entities
- **Query Optimization**: Efficient database queries and relationships
- **Transaction Management**: Database transaction handling

#### 5. Model Layer (`app/models/`)
- **Database Schema**: SQLAlchemy models defining table structures
- **Relationships**: Entity relationships and foreign key constraints
- **Data Integrity**: Database-level constraints and validations

#### 6. Core Layer (`app/core/`)
- **Configuration**: Application settings and environment management
- **Database**: Database connection and session management
- **Exceptions**: Custom exception classes and error handling

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
│   │       ├── sync_endpoints.py
│   │       ├── project_endpoints.py
│   │       └── step_endpoints.py
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
│   │   ├── list_role_model.py  # List Role entity model
│   │   ├── list_user_model.py  # List-User association model
│   │   ├── project_model.py    # Project entity model
│   │   └── step_model.py       # Step entity model
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py  # Generic repository pattern
│   │   ├── list_repository.py  # List-specific data operations
│   │   ├── item_repository.py  # Item-specific data operations
│   │   ├── user_repository.py  # User-specific data operations
│   │   ├── role_repository.py  # Role-specific data operations
│   │   ├── project_repository.py # Project-specific data operations
│   │   └── step_repository.py    # Step-specific data operations
│   │
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── list_schema.py      # List request/response schemas
│   │   ├── item_schema.py      # Item request/response schemas
│   │   ├── user_schema.py      # User request/response schemas
│   │   ├── role_schema.py      # Role request/response schemas
│   │   ├── response_schema.py  # Generic response schemas
│   │   ├── project_schema.py   # Project request/response schemas
│   │   └── step_schema.py      # Step request/response schemas
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── list_service.py     # List business logic
│   │   ├── item_service.py     # Item business logic
│   │   ├── role_service.py     # Role business logic
│   │   ├── lock_service.py     # Concurrency control
│   │   ├── notification_service.py
│   │   ├── project_service.py  # Project business logic
│   │   └── step_service.py     # Step business logic
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

### Project Management
- `POST /api/projects/` - Create a new project
- `GET /api/projects/` - Get all projects
- `GET /api/projects/{project_id}` - Get specific project details
- `PUT /api/projects/{project_id}` - Update project information
- `DELETE /api/projects/{project_id}` - Delete project

### Step Management
- `POST /api/steps/` - Create a new step
- `GET /api/steps/` - Get all steps
- `GET /api/steps/{step_id}` - Get specific step details
- `PUT /api/steps/{step_id}` - Update step information
- `DELETE /api/steps/{step_id}` - Delete step

### Locking System
- `POST /api/lists/{list_id}/lock` - Acquire lock on list
- `DELETE /api/lists/{list_id}/lock` - Release lock on list

### Synchronization
- `POST  /api/lists/{list_id}/sync` - Manual synchronization endpoint
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

### Project
- id: Integer primary key
- name: String (required)
- place_description: String (optional)
- planned_start_date: Timestamp (optional)
- planned_end_date: Timestamp (optional)
- actual_start_date: Timestamp (optional)
- actual_end_date: Timestamp (optional)
- total_materials_price: Float (optional)
- total_workers_price: Float (optional)

### Step
- id: Integer primary key
- name: String (required)
- planned_start_date: Timestamp (optional)
- planned_end_date: Timestamp (optional)
- actual_start_date: Timestamp (optional)
- actual_end_date: Timestamp (optional)
- materials_price: Float (optional)
- workers_price: Float (optional)
- project_id: Foreign key to Project
- parent_step_id: Foreign key to Step (self-referencing)

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
- 201: Created
- 204: No Content
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

## Business workflow

### A potential workflow:  
1. Project Planning: user defines project by creating a Project and breaking it down into hierarchical Steps. Each Step would have a description of the materials needed.
2. Material Aggregation: You create one or more Lists (e.g., "Hardware Store List," "Online Plumbing Orders") to gather all the Items required across all your Steps.
3. Collaborative Purchasing: You use the List entity's collaboration features to manage the purchasing process. A CLIENT can approve prices, and a WORKER can update quantities and mark items as "bought" or "delivered."
4. Work Execution: Once the Items for a Step are marked as "delivered" in your List, the work on that Step can commence.  

This approach creates a clear separation of concerns:
•Project / Step: Manages the work and schedule.
•List / Item: Manages the materials and procurement.

On front-end there would be a project of maintenance. That would consist of many steps of maintenance. there are steps that could be paralleled, or be in sequence. there are several abstractions of steps.
List entity is used as the "shopping cart" for maintenance project. The Step entity defines what work needs to be done, and the List entity helps manage the acquisition of materials (Items) needed for that work.

For example: 
- Project1:  
  - room1->walls clearing->walls coloring,  
  - room2->floors and walls clearing->floors clearing->new floors  
  - room2->floors and walls clearing->walls clearing->walls coloring  

But I don't want some tricky and hard to understand and hard to use app for final users.
More formal front-end would be something like this:  

- Project  
  - Steps:  
    - Name  
    - Price (workers)  
    - Price (materials)  
    - Period plan  
    - Period fact  
    - Items needed + quantity  
    - Photo/video of results  
    - Parent step (only one parent step)  
  - Summary  
    - Name  
    - Gantt diagram  
    - Period plan (full)  
    - Period fact (full)  
    - Price (materials full)  
    - Price (workers full)  
    - Place description  
    - Steps  
