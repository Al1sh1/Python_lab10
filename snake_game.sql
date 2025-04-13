CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    current_level INTEGER DEFAULT 1
);

CREATE TABLE user_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    score INTEGER,
    level INTEGER,
    snake_body TEXT,
    snake_direction VARCHAR(10),
    food_x INTEGER,
    food_y INTEGER,
    food_weight INTEGER,
    food_timer FLOAT,
    speed INTEGER,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);