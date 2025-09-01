CREATE TABLE global_roles (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	role_type VARCHAR(6) NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (user_id)
);
CREATE TABLE list_roles (
	id INTEGER NOT NULL, 
	role_type VARCHAR(7) NOT NULL, 
	description VARCHAR, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (role_type)
);
CREATE TABLE lists (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE list_users (
	id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	list_id INTEGER NOT NULL, 
	role_id INTEGER NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_user_list UNIQUE (user_id, list_id), 
	FOREIGN KEY(user_id) REFERENCES global_roles (user_id), 
	FOREIGN KEY(list_id) REFERENCES lists (id), 
	FOREIGN KEY(role_id) REFERENCES list_roles (id)
);
CREATE INDEX ix_list_users_id ON list_users (id);
CREATE TABLE items (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	category VARCHAR, 
	quantity INTEGER, 
	price FLOAT, 
	list_id INTEGER NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(list_id) REFERENCES lists (id)
);
CREATE TABLE locks (
	id INTEGER NOT NULL, 
	list_id INTEGER NOT NULL, 
	user_id VARCHAR NOT NULL, 
	acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (list_id), 
	FOREIGN KEY(list_id) REFERENCES lists (id), 
	FOREIGN KEY(user_id) REFERENCES global_roles (user_id)
);
CREATE INDEX ix_locks_id ON locks (id);
