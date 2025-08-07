DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id serial PRIMARY KEY,
  username varchar(50) NOT NULL,
  email varchar(100) NOT NULL,
  password varchar(100) NOT NULL,
  created_at timestamp DEFAULT now()
);

CREATE TABLE transactions (
  id serial PRIMARY KEY,
  user_id integer NOT NULL REFERENCES users(id),
  asset_name varchar(50) NOT NULL,
  amount numeric(10,2) NOT NULL,
  created_at timestamp DEFAULT now()
);

INSERT INTO users (username, email, password)
VALUES ('john_doe', 'john@example.com', 'hashedpassword');

INSERT INTO transactions (user_id, asset_name, amount)
VALUES (1, 'Bitcoin', 0.015);