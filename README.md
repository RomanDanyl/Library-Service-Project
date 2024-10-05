# Library-Service-Project

Library Service API is a Django-based web application for managing book borrowings, payments, and notifications. 
## Features

- **JWT authenticated**: Secure API access with JSON Web Tokens.
- **Admin panel /admin/**: Access the admin panel at `/admin/`.
- **Documentation is located at /api/doc/swagger/**
- **Managing books, borrowings and payments**: Includes user borrowing and return of books.
- **"CRUD" for all book objects for only admin users**
- **Telegram notifications**: Alerts for overdue borrowings, creating new borrowing
- **Stripe payments**: Secure online payments for borrowings.
- **Asynchronous task handling**: Celery is used for background tasks (sending notifications for borrowing overdue).
- **Dockerized Environment**: The project is fully dockerized for easy deployment and development.
- **Redis**: Redis is used as a message broker, running in a Docker container.

## Installation

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.9+](https://www.python.org/downloads/)

### Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/RomanDanyl/Library-Service-Project.git
   cd library-service

2. **Build and run docker containers:**
   ```bash
    docker-compose build
    docker-compose up
    ```

3. **Create a superuser**:

    ```bash
    python manage.py createsuperuser
   ```

### Usage

- **Register a user**: Use the `/api/users/register/` endpoint to register a new user.
- **Obtain tokens**: Use `/api/users/token/` to get access and refresh tokens.
- **Authenticated requests**: Include the access token in the header of your HTTP requests for authentication. Use the key "Authorize"
