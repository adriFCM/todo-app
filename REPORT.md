# Todo App – DevOps & Quality Improvement Report

## 1. Introduction

This report summarises the work done on a Django-based Todo application as part of Individual Assignment 2.  

The original project was a basic CRUD web app with minimal tests and no DevOps tooling. The main goals of this assignment were to:

- Improve **code quality** and structure (SOLID, fewer code smells),
- Add **automatic tests** with a coverage target,
- Implement a **CI/CD pipeline**,
- **Containerize** the app and deploy it to a cloud platform,
- Add **monitoring and health checks**.

The final solution delivers:

- A cleaner Django codebase with project concerns separated from business logic,
- A test suite run with `pytest` and `pytest-django` at ~90% coverage (≥ 70% enforced),
- A GitHub Actions **CI/CD workflow** that builds and pushes Docker images to Azure Container Registry (ACR) and deploys only from `main`,
- A Dockerized app running on **Azure Web App for Containers**,
- A `/health/` endpoint and a `/metrics` endpoint, plus a Prometheus configuration file for monitoring.

---

## 2. Code Quality & Design Improvements

### 2.1 Project structure and separation of concerns

The project is now clearly divided into:

- `todo_project/` – framework-level and cross-cutting concerns:
  - `settings.py` – configuration, including ALLOWED_HOSTS, installed apps, and monitoring settings.
  - `urls.py` – top-level URL routing, including the health endpoint.
  - `views.py` – project-wide utilities (currently the health check).
- `tasks/` – domain logic for the todo app:
  - `models.py` – `Task` model, with fields like `title`, `description`, `due_date`, `priority`, and `completed`.
  - `forms.py` – encapsulates validation logic (e.g. date parsing).
  - `views.py` – all task-specific actions (list, create, update, delete, toggle).
  - `urls.py` – routes for the task views.

This separation follows the **Single Responsibility Principle (SRP)**:

- The `tasks` app is responsible only for task-related behaviour.
- `todo_project` handles configuration and infrastructure concerns such as routing, monitoring, and settings.

### 2.2 Applying SOLID principles in a Django context

Within the natural constraints of Django, several changes were made to align with SOLID:

- **Single Responsibility**  
  - Health checks were moved into `todo_project/views.py` instead of mixing them with task views.
  - Forms now encapsulate input validation, so views do not manually parse and validate request data.

- **Open/Closed principle**  
  - Sorting and filtering options for the task list are controlled via whitelists, making it easy to add new fields without changing the core view logic.
  - The priority choices (Low / Medium / High) are centralised, simplifying future extensions.

- **Dependency Inversion / Interface Segregation**  
  - Views depend on Django forms and models instead of working directly with raw POST data and SQL.
  - This makes the logic easier to test and less tightly coupled.

These are modest refactorings, but they significantly improve readability, testability, and future extensibility.

### 2.3 Tests and coverage

The testing strategy uses:

- **pytest** and **pytest-django** as the primary runner,
- **pytest-cov** and `coverage.py` to measure coverage,
- A dedicated test settings module (`todo_project.settings_test`) to avoid interfering with production/runtime settings.

Tests are organised as:

- `tasks/tests.py` – unit and integration tests for the Task model, forms, and views.
- `tests/test_sanity.py` – a minimal “does the test environment work” check.
- `tests/test_healthy.py` – tests for the `/health/` endpoint.

The suite includes:

- **Unit tests** for:
  - Model defaults and behaviour (e.g. default priority, marking completed),
  - Form validation (especially due date format and required fields).

- **Integration tests** using Django’s test client for:
  - Listing tasks, posting new tasks, updating, and deleting,
  - Ensuring that state-changing operations use POST, not GET,
  - Verifying sorting/filtering combinations,
  - Verifying `/health/` returns the expected JSON.

Coverage is enforced as follows:

- `pytest` is configured to run with `--cov` options,
- A minimum coverage of **70%** is required; otherwise the command fails,
- A `coverage.xml` report is generated at the root of the repository.

A typical run shows around **90% overall coverage** with all tests passing, comfortably meeting the assignment’s “≥ 70% coverage” requirement and providing a machine-readable coverage report as a test artefact.

---

## 3. CI/CD Pipeline

### 3.1 Goals

The pipeline was designed to:

- Automatically validate every change using tests and coverage,
- Only deploy to the cloud when changes are merged into `main`,
- Build and push Docker images in a reproducible way.

### 3.2 GitHub Actions workflow

All CI/CD logic lives in:

```text
.github/workflows/ci.yml
```

The workflow defines two jobs: `test` and `deploy`.

#### 3.2.1 CI: `test` job

**Triggers:**

```yaml
on:
  push:
  pull_request:
```

The `test` job runs for any branch and on every pull request. Its main steps are:

1. **Checkout repository**  
   Using `actions/checkout` to get the source code.

2. **Set up Python 3.10**  
   With `actions/setup-python`.

3. **Install dependencies**  

   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests with coverage**  

   ```bash
   pytest
   ```

This ensures every change is automatically validated. If tests fail or coverage falls below 70%, the job fails and any pull request shows a red status.

#### 3.2.2 CD: `deploy` job

The `deploy` job is dependent on `test`:

```yaml
needs: test
if: github.ref == 'refs/heads/main'
```

It only runs when:

- the `test` job has succeeded, and  
- the commit is on the `main` branch.

Steps:

1. **Login to Azure Container Registry (ACR)**  
   Using secrets stored in GitHub:

   - `ACR_LOGIN_SERVER` (e.g. `todoacradri.azurecr.io`)
   - `ACR_USERNAME`
   - `ACR_PASSWORD`

   A `docker login` command is executed with these credentials.

2. **Build the Docker image**  

   ```bash
   docker build -t $ACR_LOGIN_SERVER/todo-app:${GITHUB_SHA} .
   docker tag $ACR_LOGIN_SERVER/todo-app:${GITHUB_SHA} \
              $ACR_LOGIN_SERVER/todo-app:latest
   ```

3. **Push image to ACR**  

   ```bash
   docker push $ACR_LOGIN_SERVER/todo-app:${GITHUB_SHA}
   docker push $ACR_LOGIN_SERVER/todo-app:latest
   ```

The use of both a unique SHA tag and the `latest` tag allows traceability of specific builds while letting the Azure Web App simply track `latest`.

### 3.3 Branching and merging strategy

Development work was carried out on a feature branch (`feat/devops-a2`) to avoid breaking `main`. The workflow was:

1. Implement changes and run tests locally,
2. Push to the feature branch,
3. Open a Pull Request into `main`,
4. Let the `test` job run for the PR,
5. Merge only after CI is green.

After merging, the `deploy` job runs for `main` and pushes the new Docker image, which the Azure Web App then uses.

This keeps `main` in a deployable state and links each deployment to a specific commit history and CI run.

---

## 4. Containerization and Cloud Deployment

### 4.1 Dockerfile

The application is containerized using a `Dockerfile` in the project root. In simplified form, it:

- Uses an official Python base image,
- Copies the application code and `requirements.txt`,
- Installs Python dependencies,
- Runs database migrations on container startup,
- Starts Django via:

  ```bash
  python manage.py runserver 0.0.0.0:8000
  ```

For local testing, the image can be built and run with:

```bash
docker build -t todo-app:dev .
docker run --rm -p 8000:8000 todo-app:dev
```

### 4.2 Azure Container Registry and Web App

The deployment target is **Azure Web App for Containers**. The main pieces are:

1. **Azure Container Registry (ACR)**  
   - Private registry to store Docker images,
   - Logs pushes from GitHub Actions (tags: commit SHA and `latest`),
   - Admin credentials used by the GitHub workflow.

2. **Azure Web App**  
   - Configured as a Linux Web App with “Container” publish,
   - Container source is ACR,
   - Image name `todo-app`, tag `latest`,
   - When `latest` is updated by CI/CD, the Web App picks up the new version (after restart).

During setup, we initially tried Azure’s Managed Identity for pulling from ACR but, due to permission constraints in the shared subscription, we switched to using ACR admin credentials, which is simpler and reliable for this assignment.

### 4.3 Django host configuration

When the container first ran on Azure, Django raised a `DisallowedHost` error because the `ALLOWED_HOSTS` setting did not include the Azure hostname. The solution was to expand `ALLOWED_HOSTS` in `settings.py` to include:

- `127.0.0.1` and `localhost` for local development,
- `.azurewebsites.net` to accept the Azure app’s domain (and any subdomain under it).

After committing this change and letting the pipeline deploy, the app became accessible in the browser via its Azure URL.

---

## 5. Monitoring and Health Checks

### 5.1 Health endpoint (`/health/`)

A simple but important addition is a dedicated health endpoint that can be used by monitoring tools or by a load balancer.

Implementation:

- In `todo_project/views.py`, a `health` view checks:
  - That the app can connect to the default database, and
  - Returns a JSON response with two fields: `status` and `database`.

- In `todo_project/urls.py`, this view is exposed as:

  ```python
  path("health/", health, name="health")
  ```

Typical response:

```json
{
  "status": "ok",
  "database": "ok"
}
```

If the database connection fails, `database` becomes `"error"` and overall `status` becomes `"degraded"`.

Tests for this endpoint live in `tests/test_healthy.py`, ensuring that `/health/` always returns the expected structure and HTTP status.

### 5.2 Metrics endpoint (`/metrics`) via `django-prometheus`

For more advanced monitoring, the app exposes metrics in the **Prometheus** format. This is achieved using the `django-prometheus` package:

- Added to `requirements.txt` and installed,
- Registered in `INSTALLED_APPS`,
- Prometheus middleware added to `MIDDLEWARE` to instrument requests,
- `django_prometheus.urls` included in `todo_project/urls.py`, which exposes `/metrics`.

Visiting `/metrics` shows various metrics such as request counts, latencies, and error counts in the standard Prometheus exposition format.

### 5.3 Prometheus configuration file

To make the monitoring setup concrete, a Prometheus configuration file is included in the repository as:

```text
monitoring/prometheus.yml
```

Example configuration:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "todo-app"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["localhost:8000"]
```

This file shows how Prometheus would be set up (locally) to scrape metrics from the app. Combined with `/metrics`, it satisfies the assignment requirement for a “monitoring configuration or dashboard file”.

---

## 6. Conclusion

Starting from a simple Django Todo application, the project has been extended into a **full DevOps-ready service**:

- The codebase has been cleaned up with a clear separation between project configuration and business logic. Small refactorings help align with SOLID principles and make the app easier to maintain.
- A proper **testing strategy** using `pytest` and `pytest-django` achieves around 90% coverage, with a strict 70% minimum enforced by the pipeline.
- A **CI/CD pipeline** built on GitHub Actions automatically runs tests for every change and deploys only from `main`, building Docker images and pushing them to Azure Container Registry.
- The application is **containerized** and deployed to **Azure Web App for Containers**, which tracks the `latest` image from ACR.
- **Monitoring** is addressed via a `/health/` endpoint and a Prometheus-compatible `/metrics` endpoint, with a sample `prometheus.yml` file included.

Together with the updated README and this report, the project now provides a complete story: from local development and testing to automated deployment and basic monitoring, meeting—and in several areas exceeding—the assignment’s requirements.
