# Todo App

To-Do-List Manager application for students and professionals that helps organize and track daily tasks efficiently, It delivers clean CRUD, optional due dates with DD/MM/YYYY validation, safe POST actions, filters & sorting, and a small test suite.

## Features

- Create / read / update / delete task
- Optional due date (strict DD/MM/YYYY when provided)
- Priority enum (Low / Medium / High) with default Low
- Filters: search (title/description), status (open/done), priority
- Sorting (whitelisted): created_at, due_date, priority, completed, title (asc/desc)
- Toggle completed via POST (CSRF-safe; no state change on GET)
- Minimal, modern UI (HTML + CSS)
- Tests for models, forms, and views

## Features
- Backend: Django (Python)
- DB: SQLite (file-based) for local development
- UI: Django templates + CSS

## Getting Started
- Python 3.10+
- Optional) requirements.txt ith Django pinned

### Set Up

1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2. Create & activate a virtualenv:
    ```bash
    python -m venv venv
    ```
    ```macOS/Linux
    source venv/bin/activate
    ```
    ```Windows (PowerShell)
    venv\Scripts\Activate
3. Install packages
    ```bash
    pip install -r requirements.txt
    ```
5. Initialize the database 
    ```bash
    python manage.py migrate
    ```
6. Start the application: 
    ```bash
    python manage.py runserver
    ```
    Open: http://127.0.0.1:8000/ → redirects to /tasks/.

### Run Test 
    
 1. ```bash
    python manage.py test
    ```

## Database
SQLite (default) 
- File is created automatically after migrate: db.sqlite3
