# Todo App

Django-based **To-Do List Manager** for students and professionals.  
Supports clean CRUD, optional due dates, filtering/sorting, and is fully wired with tests, coverage, Docker, CI/CD (GitHub Actions → Azure Container Registry → Azure Web App), and basic monitoring (health & Prometheus metrics).

---

## Features

### Application features

- Create / Read / Update / Delete tasks
- Optional due date with strict `DD/MM/YYYY` validation
- Priority enum: **Low / Medium / High** (default: Low)
- Mark tasks as **completed / not completed**
- Filters:
  - text search (title + description)
  - status (open / done)
  - priority
- Sorting (whitelisted):
  - `created_at`, `due_date`, `priority`, `completed`, `title` (asc/desc)
- Safe POST actions (no state changes on GET)
- Minimal, clean UI using Django templates + CSS

### Code quality & testing

- Django project structured into:
  - `todo_project/` – project config & cross-cutting views (e.g. `/health`)
  - `tasks/` – domain logic and task views
- Unit & integration tests (Django + pytest):
  - Model tests
  - Form tests
  - View tests (integration via Django test client)
  - Explicit health endpoint test
- Test runner: **pytest** with **pytest-django**
- Coverage:
  - Enforced in CI with `pytest-cov`
  - Threshold: **70% minimum** (build fails below)
  - Coverage report: `coverage.xml` committed in the repo

### DevOps / CI-CD

- **GitHub Actions** workflow: `.github/workflows/ci.yml`
- **CI**:
  - Trigger: every `push` and `pull_request` on any branch
  - Steps:
    - Set up Python 3.10
    - Install dependencies from `requirements.txt`
    - Run `pytest` with coverage (fails if coverage < 70%)
- **CD**:
  - Trigger: **only on pushes to `main`**
  - After tests pass:
    - Login to **Azure Container Registry (ACR)**
    - Build Docker image using the project `Dockerfile`
    - Push image to ACR as:
      - `todo-app:<commit-sha>`
      - `todo-app:latest`
  - Azure Web App is configured to run the image `todo-app:latest` from ACR

### Deployment (Azure)

- Container image registry: **Azure Container Registry (ACR)**
- Runtime: **Azure App Service – Web App for Containers (Linux)**
- Web App configured as:
  - Container type: Single container
  - Image source: Azure Container Registry
  - Image: `todo-app`
  - Tag: `latest`
  - Authentication: ACR admin credentials
- `ALLOWED_HOSTS` configured to allow the Azure Web App hostname (and `.azurewebsites.net`)

### Monitoring & health checks

- **Health endpoint**:
  - URL: `/health/`
  - Returns JSON:
    - `status`: `"ok"` or `"degraded"`
    - `database`: `"ok"` or `"error"`
  - Verifies app is up and DB is reachable
- **Metrics endpoint (Prometheus)**:
  - Using `django-prometheus`
  - URL: `/metrics`
  - Exposes metrics such as:
    - request counts
    - latency
    - error rates
  - Useful for scraping with Prometheus / visualising in Grafana
- Example Prometheus config: `monitoring/prometheus.yml`

---

## Tech Stack

- **Backend**: Django (Python 3.10)
- **Database**: SQLite (local development)
- **Frontend**: Django templates + CSS
- **Testing**: `pytest`, `pytest-django`, `pytest-cov`
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Cloud**: Azure
  - Azure Container Registry (ACR)
  - Azure Web App for Containers
- **Metrics**: `django-prometheus` + sample `prometheus.yml`

---

## Getting Started (Local)

### Prerequisites

- Python **3.10+**
- `pip`
- (Recommended) `virtualenv`
- Docker (optional, for running the container locally)

### 1. Clone the repository

```bash
git clone <repository-url>
cd todo-app
```

### 2. Create & activate a virtual enviroment 

Windows (PowerShell)

```bash
python -m venv venv
ven\Scripts\Activate
```

macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash 
pip install -r requirements.txt
```

### 4. Apply migrations & run the app 

```bash 
python manage.py migrate
python manage.py runserver
```
#### Then open:
-  http://127.0.0.1:8000/
 (root) → tasks UI


 ## Runing Test & Coverage 

 ### Quick Django test run 

 ```bash 
 python manage.py test
``` 

### Full pytest run with coverage 

```bash 
pytest
```
#### This will 
- Run Django test via pytest 
- Compute coverage with pytest-conv
- Enforce minimum 70% coverage 
- Write a coverage report to coverage.xml (included in the repo) 

## Health Check & Metrics 
Once the dev server is running: 
### Health endpoint: 

```text 
GET http://127.0.0.1:8000/health/
```
Response (example): 

```json
{
  "status": "ok",
  "database": "ok"
}`
```
### Prometheus metrics  

```text
GET http://127.0.0.1:8000/metrics
```

- Returns a text page with metrics in Prometheus exposition format.
- Locally you can run Prometheus with:
```bash 
docker run --rm -p 9090:9090 \
  -v "$(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml" \
  prom/prometheus 
  ``` 
  (Adjust the target /host if needed.) 

  ## Docker 

  ### Build the image (local) 
  From the project root 

  ```bash 
  docker build -t todo-app:dev .
  ```

  ### Run the container (local)

  ```bash
  docker run --rm -p 8000:8000 todo-app:dev
  ```
 #### Then open: 
 - http://localhost:8000/

 The container runs migrations on startup and then launches Django on 0.0.0.0:8000. 

## Deployed Application (Azure)

The application is deployed as a Docker container on **Azure Web App for Containers**.

Public URL (Azure):

https://todo-app-adri-f5fba4d3hscxdpcp.westeurope-01.azurewebsites.net/

> Note: The first request after a while may be slow because the container needs to cold-start.

Health & monitoring endpoints:

- Health check: `https://todo-app-adri-f5fba4d3hscxdpcp.westeurope-01.azurewebsites.net/health/`
- Metrics (Prometheus): `https://todo-app-adri-f5fba4d3hscxdpcp.westeurope-01.azurewebsites.net/metrics`



