
# List Editor

A modern, scalable list management application built with FastAPI that provides secure, participant-based collaboration on shared lists. The system uses UUID-based authentication and implements fine-grained access controls for collaborative list editing.

## Overview

List Editor is a collaborative list management system designed for teams and individuals who need to share and manage lists efficiently. Built with modern Python technologies, it provides a robust API for creating, sharing, and managing lists with real-time collaboration features.

### Key Highlights

- **Participant-based Access Control**: Fine-grained permissions for list creators and participants
- **Real-time Collaboration**: Concurrent editing with locking mechanisms
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

#### Technical Features
-  **RESTful API**: Clean, intuitive API design
-  **Data Validation**: Comprehensive input validation with Pydantic
-  **Error Handling**: Detailed error responses and logging
-  **Database Persistence**: SQLite with SQLAlchemy ORM
-  **Automatic Timestamps**: Creation and modification tracking
-  **CORS Support**: Cross-origin resource sharing enabled

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
   git clone <repository-url>
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
