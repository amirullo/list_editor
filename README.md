# List Editor

A simple list editor application with a robust backend architecture for managing lists and items.

## Features

- **UUID-based Access**: No traditional authentication, just use your UUID to access the system
- **Role-based Access Control**: Two roles - client (read) and worker (read/write)
- **Data Structure**: Lists with items that have name, category, quantity, and price
- **Database**: SQLite with SQLAlchemy ORM for persistent storage
- **Manual Sync System**: Explicit sync/update mechanism for clients
- **Notifications**: In-app notifications for changes made to lists
- **Concurrency Control**: FIFO locking mechanism to prevent conflicts
- **Metadata Tracking**: Creation date and last modified timestamps for all entities

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


## Installation and Setup

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
- `PUT /api/lists/items/{item_id}` - Update an item (worker role)
- `DELETE /api/lists/items/{item_id}` - Delete an item (worker role)

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

## Technical Details

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **SQLite**: File-based SQL database

