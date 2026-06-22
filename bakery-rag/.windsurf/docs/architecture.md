# Architecture Overview

## Tech Stack
| Layer        | Technology       | Reasoning                                                  |
|--------------|------------------|------------------------------------------------------------|
| Frontend     | React            | Popular, component-based, supports RTL well, large ecosystem |
| Backend      | Node.js + Express| Lightweight, efficient for REST APIs, widely used          |
| Database     | PostgreSQL       | Strong relational DB, supports complex queries, ACID compliance |

## Why PostgreSQL?
- PostgreSQL is chosen for its robust support of relational data.
- It offers advanced features like JSONB support for semi-structured data.
- ACID compliance ensures data integrity, crucial for order management.
- Strong community support and reliability.

## Additional Notes
- The backend will expose RESTful APIs.
- The frontend will consume these APIs and handle UI logic.
- The system will be designed for scalability and maintainability.
