# Todo App

A simple To-Do List manager for students and professionals to organize and track daily tasks efficiently.

The application provides:

- Clean CRUD for tasks
- Optional due dates with strict `DD/MM/YYYY` validation
- Safe POST-only actions for state changes
- Filtering, search, and sorting
- An automated test suite with coverage reporting

---

## Tech Stack

- **Backend:** Django (Python)
- **Database:** SQLite (file-based, for local development)
- **Frontend:** Django templates + CSS
- **Testing:** Django TestCase + pytest + pytest-cov

---

## Features

### Task management

- Create / Read / Update / Delete tasks  
- Mark tasks as completed / not completed  
- Toggle completion via POST (CSRF-safe; no state change on GET)

### Due dates

- Optional due date per task  
- Strict `DD/MM/YYYY` format enforced in forms  
- Clear validation error message for invalid dates  

### Priority

- Priority enum: **Low / Medium / High**  
- Default priority: **Low**

### Filtering, search & sorting

- Search by title and description  
- Filter by status: open / done  
- Filter by priority  
- Whitelisted sorting on:
  - `created_at`
  - `due_date`
  - `priority`
  - `completed`
  - `title`
- Ascending / descending order support

### UI

- Minimal, modern HTML layout  
- Simple CSS styling for readability  

---

## Getting Started

### Prerequisites

- **Python:** 3.10+
- **pip** and **virtualenv** (or similar)
- This repository cloned locally

### Setup steps

#### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create and active a virtual enviroment

macOS/Linux:
```bash
source venv/bin/activate
```

Windows (PowerShell): 
```bash
.\venv\Scripts\Activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
pip python manage.py migrate
```

### 5. Run the development server
```bash
python manage.py runserver
```
### Then open: 
- http://127.0.0.1:8000/
 → automatically redirects to
 - http://127.0.0.1:8000/tasks/

 ## Running Test
 There are two ways to run tests: Django’s built-in test runner and pytest.
 
 ### Option 1 - Django test runner 

 ```bash
python manage.py test
```
- Uses the default settings module: todo_project.settings.
- Runs tests defined in tasks/tests.py.
- Does not collect coverage or enforce any coverage threshold.

 ### Option 2 - pytest 
 Pytest is configured via pytest.ini and integrates with Django + coverage.

#### From the project root, run:
  ```bash
pytest
```
This will: 
- Use todo_project.settings_test as the Django settings module (configured in pytest.ini).
- Discover and run tests in:
    - tasks/tests.py (Django TestCase tests)
    - The tests/ directory (pytest-style tests, e.g. tests/test_sanity.py)

- Measure code coverage for the tasks app (as configured in .coveragerc).
- Show a human-readable coverage summary in the terminal.
- Generate an XML coverage report file: coverage.xml in the project root.

- Fail the test run if coverage is below 70%, via --cov-fail-under=70 in pytest.ini.

## Database
The project uses SQLite by default:
- The database file db.sqlite3 is created automatically when you run:

```bash
python manage.py migrate
````


