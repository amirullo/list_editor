
# List Editor

A list management application that provides secure, project-based collaboration on shared lists and steps.

## Overview

List Editor is a collaborative project management system designed for teams and individuals who need to share and manage projects, lists, and steps efficiently. Built with modern Python technologies, it provides a robust API for creating, sharing, and managing projects with integrated collaboration features.

### Key Highlights

- **Project-based Access Control**: Fine-grained permissions for project creators and participants, inherited by associated lists and steps.
- **Collaboration**: Concurrent editing with locking mechanisms for lists.
- **User ID-based Authentication**: Secure login with internal and external user IDs.
- **RESTful API**: Clean, well-documented API endpoints.
- **Scalable Architecture**: Modular design following clean architecture principles.

## Features

### Core Functionality

#### Project Management
- **Create Projects**: Users can create new projects.
- **Project Ownership**: Each project has a designated creator with special privileges.
- **Participant Management**: Project creators can add/remove participants to their projects.
- **Project Updates**: All participants can modify project metadata.
- **Project Deletion**: Only creators can permanently delete projects.
- **Project Details**: Projects can include a name, planned and actual periods, total material and worker prices, and a place description.

#### List Management
- **Create Lists**: Users can create new lists associated with a project.
- **List Access**: Access to lists is inherited from the parent project.
- **List Updates**: All project participants can modify list metadata.
- **List Deletion**: Only project participants with appropriate permissions can delete lists.
- **List Details**: Lists can include total price, total delivery period, and a flat address.
- **Store Locations**: Lists can include a map with store addresses.

#### Item Management
- **Add Items**: All project participants can add items to lists within their accessible projects.
- **Update Items**: Modify item details (name, category, quantity, price).
- **Delete Items**: Remove items from lists.
- **Item Categorization**: Organize items by categories.
- **Price Tracking**: Track item prices and quantities.
- **Link Parsing**: Parse item links to extract photo, price, delivery price, and delivery period.
- **Store Information**: Items can be associated with a store, including its address and distance.
- **Item Status**: Items have flags for "approved" (worker), "bought" (client/worker), and "delivered" (worker).

#### Step Management
- **Create Steps**: Break down a project into steps, each with a name, planned and actual periods, material and worker prices, required items, and photos/videos of the results.
- **Step Access**: Access to steps is inherited from the parent project.
- **Hierarchical Steps**: Steps can have a parent step, allowing for complex project structures.
- **Gantt Chart**: Visualize the project timeline with a Gantt diagram (conceptual, not implemented in API).

#### Collaboration Features
- **Project Participant Access**: Share projects with specific users, granting them access to all associated lists and steps.
- **Concurrent Editing**: Multiple users can edit lists simultaneously.
- **Lock Management**: FIFO locking system prevents conflicts for lists.
- **Real-time Notifications**: In-app notifications for list changes (conceptual, not fully implemented in API).
- **Activity Tracking**: Audit trail for all modifications (conceptual, not fully implemented in API).

#### Security & Access Control
- **User ID Authentication**: Secure login using an external ID from the `X-User-ID` header, with all subsequent operations using an internal integer ID.
- **Role-based Permissions**: Project-level roles (`CREATOR`, `USER`) define access.
- **Access Inheritance**: Lists and Steps inherit access permissions from their parent Project.
- **Access Validation**: Strict access control on all operations.
- **Data Isolation**: Users only see projects, lists, and steps they have access to.

#### Technical & Utility Features
- **RESTful API**: Clean, intuitive API design.
- **Data Validation**: Comprehensive input validation with Pydantic.
- **Error Handling**: Detailed error responses and logging.
- **Database Persistence**: PostgreSQL with SQLAlchemy ORM.
- **Automatic Timestamps**: Creation and modification tracking.
- **CORS Support**: Cross-origin resource sharing enabled.
- **Containerization**: Docker support for easy deployment.
- **Logging**: Centralized application logging and monitoring.
- **Helper Functions**: Common utility functions and custom validators.

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
- **Endpoints**: FastAPI route handlers for HTTP requests.
- **Dependencies**: Dependency injection for services and authentication.
- **Request/Response**: HTTP request processing and response formatting.

#### 2. Schema Layer (`app/schemas/`)
- **Data Validation**: Pydantic models for request/response validation.
- **Type Safety**: Strong typing for API contracts.
- **Serialization**: Data transformation between layers.

#### 3. Service Layer (`app/services/`)
- **Business Logic**: Core application logic and workflows.
- **Data Orchestration**: Coordination between multiple repositories.
- **Validation**: Business rule validation and enforcement.
- **Notifications**: User notification and messaging services.

#### 4. Repository Layer (`app/repositories/`)
- **Data Access**: Database operations and query management.
- **CRUD Operations**: Create, Read, Update, Delete operations for entities.
- **Query Optimization**: Efficient database queries and relationships.
- **Transaction Management**: Database transaction handling.

#### 5. Model Layer (`app/models/`)
- **Database Schema**: SQLAlchemy models defining table structures.
- **Relationships**: Entity relationships and foreign key constraints.
- **Data Integrity**: Database-level constraints and validations.

#### 6. Core Layer (`app/core/`)
- **Configuration**: Application settings and environment management.
- **Database**: Database connection and session management.
- **Exceptions**: Custom exception classes and error handling.

### Design Principles

- **KISS (Keep It Simple, Stupid)**: Simple, maintainable solutions.
- **YAGNI (You Aren't Gonna Need It)**: Implement only what's needed.
- **Open/Closed Principle**: Extensible design with minimal modifications.
- **Single Responsibility**: Each component has a single, well-defined purpose.
- **Dependency Injection**: Loose coupling through dependency injection.

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
│   │       ├── project_endpoints.py # Updated
│   │       ├── step_endpoints.py    # Updated
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
│   │   ├── project_model.py    # Project entity model
│   │   ├── project_user_model.py # New: Project-User association model
│   │   ├── project_role_model.py # New: Project Role entity model
│   │   └── step_model.py       # Step entity model
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py  # Generic repository pattern
│   │   ├── list_repository.py  # List-specific data operations
│   │   ├── item_repository.py  # Item-specific data operations
│   │   ├── user_repository.py  # User-specific data operations
│   │   ├── project_repository.py # Project-specific data operations
│   │   ├── project_user_repository.py # New: Project-User association repository
│   │   └── step_repository.py    # Step-specific data operations
│   │
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── list_schema.py      # List request/response schemas
│   │   ├── item_schema.py      # Item request/response schemas
│   │   ├── user_schema.py      # User request/response schemas
│   │   ├── response_schema.py  # Generic response schemas
│   │   ├── project_schema.py   # Project request/response schemas
│   │   └── step_schema.py      # Step request/response schemas
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── list_service.py     # List business logic
│   │   ├── item_service.py     # Item business logic
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

### Project Management
- `POST /api/projects/` - Create a new project.
- `GET /api/projects/` - Get all projects for the authenticated user.
- `GET /api/projects/{project_id}` - Get specific project details.
- `PUT /api/projects/{project_id}` - Update project information.
- `DELETE /api/projects/{project_id}` - Delete project (creator only).
- `POST /api/projects/{project_id}/users` - Add a user to a project by their external ID (project creator only).
- `DELETE /api/projects/{project_id}/users` - Remove a user from a project by their external ID (project creator only).

### List Management
- `POST /api/lists/` - Create a new list, associated with a `project_id`.
- `GET /api/lists/project/{project_id}` - Get all lists for a specific project.
- `GET /api/lists/{list_id}` - Get specific list details (requires project access).
- `PUT /api/lists/{list_id}` - Update list information (requires project access).
- `DELETE /api/lists/{list_id}` - Delete list (requires project access).

### Item Management
- `POST /api/lists/{list_id}/items` - Create new item in list (requires project access).
- `GET /api/lists/{list_id}/items` - Get all items in list (requires project access).
- `PUT /api/lists/{list_id}/items/{item_id}` - Update item (requires project access).
- `DELETE /api/lists/{list_id}/items/{item_id}` - Delete item (requires project access).

### Step Management
- `POST /api/steps/` - Create a new step, associated with a `project_id`.
- `GET /api/steps/` - Get all steps (requires project access).
- `GET /api/steps/{step_id}` - Get specific step details (requires project access).
- `PUT /api/steps/{step_id}` - Update step information (requires project access).
- `DELETE /api/steps/{step_id}` - Delete step (requires project access).

### Locking System
- `POST /api/lists/{list_id}/lock` - Acquire lock on list (requires project access).
- `DELETE /api/lists/{list_id}/lock` - Release lock on list (requires project access).

### Synchronization
- `POST  /api/lists/{list_id}/sync` - Manual synchronization endpoint.
- `GET /api/sync/notifications` - Get notifications for changes.

### Role Management
- `POST /api/roles/global` - Create a new global role for a user.
- `GET /api/roles/global/{user_internal_id}` - Get the global role for a user.

## Data Models

### User
- `id`: Integer primary key (internal ID).
- `external_id`: String (unique, for login).

### Project
- `id`: Integer primary key.
- `name`: String (required).
- `place_description`: String (optional).
- `planned_start_date`: Timestamp (optional).
- `planned_end_date`: Timestamp (optional).
- `actual_start_date`: Timestamp (optional).
- `actual_end_date`: Timestamp (optional).
- `total_materials_price`: Float (optional).
- `total_workers_price`: Float (optional).

### ProjectUser (Association)
- `user_id`: Foreign key to User (internal ID).
- `project_id`: Foreign key to Project.
- `role_type`: Enum (`CREATOR`, `USER`).

### ProjectRole
- `id`: Integer primary key.
- `role_type`: Enum (`CREATOR`, `USER`).
- `description`: String (optional).

### List
- `id`: Integer primary key.
- `name`: String (required).
- `description`: Text (optional).
- `project_id`: Foreign key to Project (required).
- `created_at`: Timestamp.
- `updated_at`: Timestamp.

### Item
- `id`: Integer primary key.
- `name`: String (required).
- `description`: Text (optional).
- `quantity`: Integer (default: 1).
- `price`: Float (optional).
- `category`: String (optional).
- `list_id`: Foreign key to List.

### Step
- `id`: Integer primary key.
- `name`: String (required).
- `planned_start_date`: Timestamp (optional).
- `planned_end_date`: Timestamp (optional).
- `actual_start_date`: Timestamp (optional).
- `actual_end_date`: Timestamp (optional).
- `materials_price`: Float (optional).
- `workers_price`: Float (optional).
- `project_id`: Foreign key to Project.
- `parent_step_id`: Foreign key to Step (self-referencing).

### Lock
- `id`: Integer primary key.
- `list_id`: Foreign key to List.
- `holder_id`: Foreign key to User (internal ID).

### GlobalRole
- `id`: Integer primary key.
- `user_id`: Foreign key to User (internal ID).
- `role_type`: Enum (`CLIENT`, `WORKER`).


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
- `CLIENT`: Can change the price of an item.
- `WORKER`: Can change the quantity, approved, bought, and delivered status of an item.

### Project roles (Global role restrictions override Project role privileges)
- `CREATOR`: The user who created the project. Has full access to the project and all associated lists and steps. Can add/remove other users to/from the project.
- `USER`: An additional user added to the project. Has access to the project and all associated lists and steps.

### Access Inheritance
- **Lists** inherit access from their parent **Project**.
- **Steps** inherit access from their parent **Project**.

### Examples: 
- `CREATOR` + `CLIENT`: Can manage the project, lists, and steps. Can change item prices, but not item quantities or status fields (`approved`, `bought`, `delivered`).
- `CREATOR` + `WORKER`: Can manage the project, lists, and steps. Can change item quantities and status fields, but not item prices.
- `USER` + `CLIENT`: Can access the project, lists, and steps. Can change item prices, but not item quantities or status fields.
- `USER` + `WORKER`: Can access the project, lists, and steps. Can change item quantities and status fields, but not item prices.

## Business workflow

### A potential workflow:  
1. **Project Planning**: A user defines a project by creating a Project and breaking it down into hierarchical Steps. Each Step would have a description of the materials needed.
2. **Material Aggregation**: Within the project, you create one or more Lists (e.g., "Hardware Store List," "Online Plumbing Orders") to gather all the Items required across all your Steps.
3. **Collaborative Purchasing**: Project participants use the List entity's collaboration features to manage the purchasing process. A `CLIENT` can approve prices, and a `WORKER` can update quantities and mark items as "bought" or "delivered."
4. **Work Execution**: Once the Items for a Step are marked as "delivered" in your List, the work on that Step can commence.  

This approach creates a clear separation of concerns:
- **Project / Step**: Manages the work and schedule.
- **List / Item**: Manages the materials and procurement.

On the front-end, there would be a project of maintenance. That would consist of many steps of maintenance. There are steps that could be paralleled, or be in sequence. There are several abstractions of steps.
The List entity is used as the "shopping cart" for a maintenance project. The Step entity defines what work needs to be done, and the List entity helps manage the acquisition of materials (Items) needed for that work.

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
