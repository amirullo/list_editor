-- ==============================
-- PostgreSQL DDL from SQLite
-- ==============================

CREATE TABLE global_roles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    role_type VARCHAR(6) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (user_id)
);

CREATE TABLE list_roles (
    id SERIAL PRIMARY KEY,
    role_type VARCHAR(7) NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (role_type)
);

CREATE TABLE lists (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE list_users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    list_id INT NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT unique_user_list UNIQUE (user_id, list_id),
    FOREIGN KEY (user_id) REFERENCES global_roles(user_id),
    FOREIGN KEY (list_id) REFERENCES lists(id),
    FOREIGN KEY (role_id) REFERENCES list_roles(id)
);

CREATE INDEX ix_list_users_id ON list_users (id);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    category VARCHAR,
    quantity INT,
    price NUMERIC, -- better precision than FLOAT
    list_id INT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES lists(id)
);

CREATE TABLE locks (
    id SERIAL PRIMARY KEY,
    list_id INT NOT NULL,
    user_id VARCHAR NOT NULL,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (list_id),
    FOREIGN KEY (list_id) REFERENCES lists(id),
    FOREIGN KEY (user_id) REFERENCES global_roles(user_id)
);

CREATE INDEX ix_locks_id ON locks (id);
