# Initial Database Schema

| Table   | Column       | Type          | Description                    |
|---------|--------------|---------------|-------------------------------|
| Users   | id           | SERIAL PRIMARY KEY | Unique user identifier       |
|         | username     | VARCHAR(50)   | User's login name             |
|         | email        | VARCHAR(100)  | User's email address          |
|         | password_hash| VARCHAR(255)  | Hashed password               |
|         | created_at   | TIMESTAMP     | Account creation timestamp    |

| Products| id           | SERIAL PRIMARY KEY | Unique product identifier    |
|         | name         | VARCHAR(100)  | Product name                 |
|         | description  | TEXT          | Product description          |
|         | price        | DECIMAL(10,2) | Product price                |
|         | created_at   | TIMESTAMP     | Product creation timestamp   |

| Orders  | id           | SERIAL PRIMARY KEY | Unique order identifier      |
|         | user_id      | INTEGER       | Foreign key to Users          |
|         | product_id   | INTEGER       | Foreign key to Products       |
|         | quantity     | INTEGER       | Number of products ordered    |
|         | total_price  | DECIMAL(10,2) | Total price of the order      |
|         | order_date   | TIMESTAMP     | Date and time of order        |
|         | status       | VARCHAR(50)   | Order status (e.g., pending, completed) |
