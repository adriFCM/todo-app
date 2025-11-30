# Todo App – DevOps & Quality Improvement Report 
## 1. Introduction

This report summarises the main improvements made to a Django-based Todo application for Individual Assignment 2. The original app was a simple CRUD project with minimal tests and no DevOps tooling.

The assignment required:
- Better **code quality** (refactoring + SOLID),
- **Automated tests** with ≥70% coverage and a coverage report,
- A working **CI/CD pipeline**,
- **Containerization** and deployment to a cloud platform,
- Basic **monitoring** and health checks.

The final system now has a clean Django structure, a robust test suite (≈90% coverage), GitHub Actions CI/CD, Docker images pushed to Azure Container Registry (ACR), an Azure Web App for Containers, and `/health` + `/metrics` endpoints with a Prometheus config file.

---

## 2. Code Quality & Design Improvements

### 2.1 Project structure

The codebase is organised into:

- `todo_project/` – framework and infrastructure:
  - `settings.py`: configuration (ALLOWED_HOSTS, installed apps, monitoring).
  - `urls.py`: root URL routing, including `tasks` and `/health`/`/metrics`.
  - `views.py`: project-wide utilities (health check).
- `tasks/` – domain logic:
  - `models.py`: `Task` model with title, description, due date, priority, completed.
  - `forms.py`: input validation and parsing (e.g. date format).
  - `views.py`: CRUD and list views, plus filtering/sorting and toggle-completed.
  - `urls.py`: task routes, mounted at `/`.

This separation keeps project configuration and business logic independent and easier to maintain.

### 2.2 SOLID in a Django context

Refactorings applied the spirit of SOLID without overcomplicating Django’s patterns:

- **Single Responsibility**  
  - Health logic moved to `todo_project/views.py`.  
  - Validation handled in `forms.py` instead of ad‑hoc checks in views.

- **Open/Closed**  
  - Sorting and filtering are driven by whitelisted fields. Adding a new sortable field usually means just adding it to the whitelist, not rewriting the view.
  - Priority values are defined centrally, so new priorities can be added without changing scattered magic strings.

- **Dependency Inversion / Interface Segregation**  
  - Views depend on Django forms and models rather than raw request data or SQL, making it easier to swap validation or storage layers later if needed.

The result is shorter, more focused views, less duplication, and easier testing.

### 2.3 Testing strategy and coverage

Testing is based on `pytest` and `pytest-django` with `pytest-cov`:

- `pytest.ini` points to `todo_project.settings_test` so tests use a dedicated configuration.
- Dependencies for testing are listed in `requirements.txt`.

Tests are organised as:

- `tasks/tests.py`  
  - Model tests: default values, completion flag, ordering.
  - Form tests: due date validation, required fields, priority handling.
  - View tests: list/create/update/delete/toggle; correct redirects; only POST for state‑changing operations; filters and sorting combinations.

- `tests/test_sanity.py`  
  - Simple sanity check to verify that the test environment and Django setup are correct.

- `tests/test_healthy.py`  
  - Checks that `/health/` returns HTTP 200 and the expected JSON keys.

The CI and local runs use:

```bash
pytest
```

which runs tests with coverage and generates `coverage.xml`. Coverage is enforced at 70% minimum; the current suite reaches ~90% overall coverage, satisfying the assignment requirement and providing a machine‑readable report.

---

## 3. CI/CD Pipeline

### 3.1 Goals

The pipeline was designed to:

- Run tests and coverage automatically on every change,
- Prevent deployment if tests fail,
- Build and publish Docker images,
- Deploy only changes from the `main` branch.

### 3.2 GitHub Actions workflow

The pipeline lives in `.github/workflows/ci.yml` and defines two jobs: `test` and `deploy`.

#### 3.2.1 `test` job (CI)

**Triggers**: `push` and `pull_request` on any branch.

Main steps:

1. Check out the code (`actions/checkout`).
2. Set up Python 3.10 (`actions/setup-python`).
3. Install dependencies: `pip install -r requirements.txt`.
4. Run `pytest` (with coverage and Django integration).

If tests or coverage fail, the job fails and pull requests show a red status.

#### 3.2.2 `deploy` job (CD)

The `deploy` job:

- Depends on `test` (`needs: test`),
- Runs only on `main` (`if: github.ref == 'refs/heads/main'`).

Steps:

1. **Login to ACR** using GitHub secrets (`ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`).
2. **Build Docker image** and tag it with both the commit SHA and `latest`:
   ```bash
   docker build -t $ACR_LOGIN_SERVER/todo-app:${GITHUB_SHA} .
   docker tag $ACR_LOGIN_SERVER/todo-app:${GITHUB_SHA} \
              $ACR_LOGIN_SERVER/todo-app:latest
   ```
3. **Push image** to ACR with both tags.

Only after a successful test run on `main` do new images get pushed, which keeps deployments safe and traceable.

### 3.3 Branching strategy

Work was done on a feature branch `feat/devops-a2`:

1. Implement changes on the feature branch.
2. Push and open a Pull Request into `main`.
3. Let CI run (`test` job).
4. Merge only after green checks.
5. The merge into `main` triggers `deploy` and updates the running app.

This keeps `main` always in a deployable state and links every deployment to a PR and CI run.

---

## 4. Containerization & Azure Deployment

### 4.1 Dockerfile

The app is packaged using a root‑level `Dockerfile`. In summary, it:

- Uses an official Python base image,
- Copies application code and `requirements.txt`,
- Installs dependencies,
- Runs migrations on start,
- Launches Django with:
  ```bash
  python manage.py runserver 0.0.0.0:8000
  ```

Local usage:

```bash
docker build -t todo-app:dev .
docker run --rm -p 8000:8000 todo-app:dev
```

### 4.2 Azure Container Registry and Web App

Deployment targets Azure:

1. **Azure Container Registry (ACR)**  
   - Stores private images `todo-app:<sha>` and `todo-app:latest`.  
   - Receives pushes from the GitHub Actions `deploy` job.

2. **Azure Web App for Containers**  
   - Linux Web App configured to use ACR as the source.
   - Image: `todo-app`, tag: `latest`.  
   - When the GitHub workflow pushes a new `latest`, the Web App can be restarted to run the newest version.

Due to limited permissions in the shared subscription, configuration uses **ACR admin credentials** instead of Managed Identity, which keeps the setup simple and reliable for this assignment.

### 4.3 ALLOWED_HOSTS fix

When the container first ran on Azure, Django raised a `DisallowedHost` error because the Azure hostname was not in `ALLOWED_HOSTS`. The fix was to update `settings.py`:

```python
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".azurewebsites.net",
]
```

After committing and merging this change, the pipeline deployed a new image and the app became accessible via its Azure URL.

---

## 5. Monitoring & Health Checks

### 5.1 `/health` endpoint

A simple health check endpoint provides quick status:

- Implemented in `todo_project/views.py`.
- Checks database connectivity and returns JSON:
  ```json
  { "status": "ok", "database": "ok" }
  ```
  or `"degraded"` if the DB check fails.
- Exposed in `todo_project/urls.py` as:
  ```python
  path("health/", health, name="health")
  ```

`tests/test_healthy.py` verifies that the endpoint responds with HTTP 200 and the expected JSON structure.

### 5.2 `/metrics` endpoint and Prometheus

For metrics, the project uses `django-prometheus`:

- Added to `INSTALLED_APPS` and `MIDDLEWARE`.
- `django_prometheus.urls` included in `todo_project/urls.py`.

This exposes `/metrics`, which outputs Prometheus‑compatible metrics such as request counts and latencies.

A sample Prometheus configuration is included in `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "todo-app"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["localhost:8000"]
```

This file demonstrates how Prometheus would scrape the app in a local or lab environment, fulfilling the “monitoring configuration or dashboard file” requirement.

---

## 6. Conclusion

The original Todo app has been transformed into a small but complete DevOps pipeline:

- Code is structured with clearer responsibilities and fewer smells, applying SOLID ideas where appropriate.
- Automated tests with `pytest` and `pytest-django` reach around 90% coverage, with a strict 70% minimum enforced by CI and a `coverage.xml` report.
- A GitHub Actions pipeline runs tests on every change and deploys only on `main`, building and pushing Docker images to Azure Container Registry.
- The app is containerized and deployed on Azure Web App for Containers, using the `latest` image tag from ACR.
- Monitoring is covered via `/health` for quick checks and `/metrics` + `prometheus.yml` for metrics and observability.

Together with the updated README and this report, the repository clearly documents the improvements, the CI/CD pipeline, and the monitoring setup required for the assignment.
