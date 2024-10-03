"# Library-Service-Project"

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
- **Redis**: Redis is used as a message broker, running in a Docker container.

## Installation

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (for Redis)
- [Python 3.9+](https://www.python.org/downloads/)

### Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/YourUsername/library-service.git
   cd library-service

2. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
    ```

3. **Run Redis in Docker**:

    ```bash
    docker run -d --name redis -p 6379:6379 redis:latest
    ```

4. **Run database migrations**:

    ```bash
    python manage.py migrate
    ```

5. **Create a superuser**:

    ```bash
    python manage.py createsuperuser
   ```
 
6. **Start the development server**:

    ```bash
    python manage.py runserver
    ```  

7. **Start the Celery worker**:

    ```bash
    celery -A library worker --loglevel=info
    ```

8. **Start the Celery beat**:

    ```bash
    celery -A library beat --loglevel=info
    ```
### Usage

- **Register a user**: Use the `/api/user/register/` endpoint to register a new user.
- **Obtain tokens**: Use `/api/user/token/` to get access and refresh tokens.
- **Authenticated requests**: Include the access token in the header of your HTTP requests for authentication. Use the key "Authorize"
