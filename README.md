# List Editor

A simple list editor application with a robust backend architecture for managing lists and items by 2 roles, client and worker (for house maintenance).

## Main Features:
- **UUID-based Access:** Users access the system using a unique UUID instead of traditional authentication.
- **Role-based Access Control:** Supports two roles—client (read-only) and worker (read/write).
- **Data Structure:** Lists contain items with attributes such as name, category, quantity, and price.
- **Database:** Utilizes SQLite with SQLAlchemy ORM for data persistence.
- **Manual Sync System:** Allows explicit synchronization and updates by clients.
- **Notifications:** Provides in-app notifications for list changes.
- **Concurrency Control:** Employs a FIFO locking mechanism to manage concurrent edits.
- **Metadata Tracking:** Tracks creation and modification timestamps for all entities.
- **Race Condition Handling:** Implements SQLite-compatible locking mechanisms in the Lock Service to minimize race conditions:
  - Uses atomic INSERT or UPDATE operations for lock acquisition.
  - Provides best-effort concurrency control suitable for the current SQLite backend.
  - Designed with future scalability in mind, allowing for easy transition to more robust database systems like PostgreSQL for enhanced concurrency support.

## Project Structure

The project follows a clean architecture pattern with separation of concerns:

```
app/
├── models/         # Database models (SQLAlchemy)
├── schemas/        # Data validation schemas (Pydantic)
├── services/       # Business logic
├── repositories/   # Data access layer
├── api/            # API endpoints
│   └── endpoints/  # Route handlers
├── core/           # Core configuration
└── utils/          # Utility functions
```

## Getting Started

### Prerequisites:
- Python 3.7+
- Docker (for containerized deployment)
- Git (for cloning the repository)

### Installation and Setup

1. Clone the repository
2. Install dependencies:
```
pip install fastapi uvicorn sqlalchemy pydantic
```

3. Run the application:
```
docker build -t list_editor:test .
docker run -p 8000:8000 list_editor:test
```

4. Run script examples (interact with) :
```
python ./scripts/create_list.py
python ./scripts/worker.py
```

## API Endpoints

### Lists
- `GET /api/lists` - Get all lists
- `GET /api/lists/{list_id}` - Get a specific list
- `POST /api/lists` - Create a new list (client role)
- `PUT /api/lists/{list_id}` - Update a list (worker role)
- `DELETE /api/lists/{list_id}` - Delete a list (worker role)

### Items
- `POST /api/lists/{list_id}/items` - Add an item to a list (worker role)
- `PUT /api/lists/{list_id}/items/{item_id}` - Update an item (worker role)
- `DELETE /api/lists/{list_id}/items/{item_id}` - Delete an item (worker role)

### Locks
- `POST /api/lists/{list_id}/lock` - Acquire a lock on a list (worker role)
- `DELETE /api/lists/{list_id}/lock` - Release a lock (worker role)

### Roles
- `POST /api/roles` - Assign a role to the current user
- `GET /api/roles` - Get the current user's role

### Sync
- `GET /api/sync/notifications` - Get notifications for changes

## Using the API

1. First, assign a role to your user (client or worker)
2. As a client, you can create lists and view them
3. As a worker, you can:
   - Acquire a lock on a list
   - Make changes to the list
   - Release the lock when done

## Concurrency Model

The application uses a FIFO locking mechanism:
- Only one worker can edit a list at a time
- Locks must be explicitly acquired and released
- If a list is locked, other workers will receive an error

## Technical Stack:

- **Framework:** FastAPI
- **Database:** SQLite (with plans to support more robust systems like PostgreSQL in the future)
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Authentication:** UUID-based (custom implementation)
- **Containerization:** Docker

## Current Limitations and Future Improvements:
- The current SQLite database may have limitations for high-concurrency scenarios. Future versions may migrate to PostgreSQL for better performance and concurrency support.
- API versioning is not yet implemented but is planned for future releases to ensure backward compatibility as new features are added.
- While basic concurrency control is implemented, more robust solutions may be needed as the user base grows.
- Comprehensive unit and integration tests are planned for future development to ensure reliability and ease of maintenance.

